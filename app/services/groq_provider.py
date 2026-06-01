"""
Groq provider orchestration for role-based key selection.

Direct search uses GROQ_API_KEY_SEARCH_DEDICATED only. It does not rotate,
cool down, or fall back to quiz or worker keys.
"""

import os
import threading
import time

# Default 429 cooldown: 2 minutes. Override via GROQ_COOLDOWN_SECONDS env var.
_DEFAULT_COOLDOWN_SECONDS = 120.0


# ── Custom exceptions ────────────────────────────────────────────────────────

class GroqRateLimitError(Exception):
    """Raised when a Groq API call returns HTTP 429 Too Many Requests."""

    def __init__(self, message="Groq rate limit exceeded (429)", key=None):
        super().__init__(message)
        self.key = key  # the specific key that was rate-limited


class AllWorkerKeysCoolingDown(Exception):
    """All worker-pool keys are currently in cooldown.

    The caller (enrichment worker) should sleep and retry later rather than
    crashing or spinning.
    """


# ── Internal provider pool ───────────────────────────────────────────────────

class _ProviderPool:
    """Thread-safe Groq key pool.  Instantiated once as a module-level singleton."""

    def __init__(self):
        self._lock = threading.Lock()
        # key → expiry timestamp (time.monotonic())
        self._cooldowns: dict[str, float] = {}
        # key → last 429 timestamp (time.monotonic())
        self._last_429_timestamps: dict[str, float] = {}
        # key → count of consecutive 429s
        self._consecutive_429s: dict[str, int] = {}
        # round-robin cursor for worker keys
        self._worker_idx: int = 0

    # ── Key resolution ───────────────────────────────────────────────────────

    def _search_key(self) -> str | None:
        return (
            os.environ.get("GROQ_API_KEY_SEARCH_PRIMARY")
            or os.environ.get("GROQ_API_KEY_SEARCH")
            or os.environ.get("GROQ_API_KEY")
        )

    def _quiz_keys(self) -> list[str]:
        """Return ordered list: KEY2 first, then backup quiz keys KEY7-10."""
        primary = (
            os.environ.get("GROQ_API_KEY_QUIZ")
            or os.environ.get("GROQ_API_KEY")
        )
        backups = [
            os.environ.get(f"GROQ_API_KEY_QUIZ_BACKUP_{i}")
            for i in range(1, 5)
        ]
        keys = [k for k in ([primary] + backups) if k]
        return keys

    def _worker_keys(self) -> list[str]:
        keys = [
            os.environ.get(f"GROQ_API_KEY_WORKER_{i}")
            for i in range(1, 5)
        ]
        keys = [k for k in keys if k]
        if not keys:
            # Graceful degradation: fall back to the single legacy key so
            # existing single-key deployments keep working.
            legacy = os.environ.get("GROQ_API_KEY")
            if legacy:
                keys = [legacy]
        return keys

    def model(self) -> str:
        return os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

    # ── Cooldown management ──────────────────────────────────────────────────

    def _is_cooling(self, key: str) -> bool:
        return time.monotonic() < self._cooldowns.get(key, 0.0)

    def mark_rate_limited(self, key: str, cooldown_seconds: float | None = None) -> None:
        """Record that *key* returned 429 and should not be used for a while.

        Applies adaptive cooldowns:
          - First 429: 5 minutes (300 seconds)
          - Repeated 429 (within 15 minutes of the last one): 15 minutes (900 seconds)
        """
        if not key or key == os.getenv("GROQ_API_KEY_SEARCH_DEDICATED"):
            return
        with self._lock:
            now = time.monotonic()
            if cooldown_seconds is None:
                last_time = self._last_429_timestamps.get(key, 0.0)
                # If rate-limited recently (within 15 minutes)
                if now - last_time < 900.0:
                    self._consecutive_429s[key] = self._consecutive_429s.get(key, 0) + 1
                else:
                    self._consecutive_429s[key] = 1

                self._last_429_timestamps[key] = now

                # Apply adaptive cooldown
                if self._consecutive_429s[key] > 1:
                    cooldown_seconds = 900.0  # 15 minutes
                else:
                    cooldown_seconds = 300.0  # 5 minutes
            else:
                self._last_429_timestamps[key] = now
                self._consecutive_429s[key] = self._consecutive_429s.get(key, 0) + 1

            self._cooldowns[key] = now + cooldown_seconds

    def reset_cooldown(self, key: str) -> None:
        """Remove *key* from cooldown (call after a successful request if needed)."""
        with self._lock:
            self._cooldowns.pop(key, None)

    # ── Public key accessors ─────────────────────────────────────────────────

    def get_search_key(self) -> str:
        return os.getenv("GROQ_API_KEY_SEARCH_DEDICATED")

    def get_quiz_key(self) -> str:
        """Return the best available key for quiz generation requests.

        Primary: KEY2 (GROQ_API_KEY_QUIZ)
        Backups: KEY7-10 (GROQ_API_KEY_QUIZ_BACKUP_1..4)
        Last resort: primary key even if cooling (caller handles 429)

        Worker keys are NOT used for quiz requests — they are reserved
        exclusively for background enrichment cache saturation.
        """
        with self._lock:
            quiz_keys = self._quiz_keys()
            for key in quiz_keys:
                if not self._is_cooling(key):
                    return key
            # All quiz keys cooling — fall back to worker keys to avoid
            # a complete blackout, but this is a rare last-resort path
            for key in self._worker_keys():
                if not self._is_cooling(key):
                    return key
            # Every key cooling — return primary quiz key; caller handles 429
            return quiz_keys[0] if quiz_keys else ""

    def get_worker_key(self) -> str:
        """Return a healthy worker key, using the same key steadily until it
        fails or becomes rate-limited, only then rotating to another key.

        Raises AllWorkerKeysCoolingDown when every key in the pool is in
        its cooldown window or capacity reservation limit is hit — 
        caller should sleep and retry later.
        """
        with self._lock:
            keys = self._worker_keys()
            if not keys:
                raise AllWorkerKeysCoolingDown("No worker keys configured.")
            
            # Capacity reservation for live search
            healthy_worker_keys = sum(1 for k in keys if not self._is_cooling(k))
            MIN_RESERVED_KEYS = 1
            if healthy_worker_keys <= MIN_RESERVED_KEYS:
                raise AllWorkerKeysCoolingDown(
                    f"Worker capacity reservation limit reached. "
                    f"Healthy worker keys: {healthy_worker_keys}, MIN_RESERVED_KEYS: {MIN_RESERVED_KEYS}."
                )

            n = len(keys)
            
            # 1. Try to use the current index key if it is healthy
            current_key = keys[self._worker_idx % n]
            if not self._is_cooling(current_key):
                return current_key
            
            # 2. If the current key is cooling, find the next healthy key and stick to it
            for attempt in range(n):
                idx = (self._worker_idx + attempt) % n
                key = keys[idx]
                if not self._is_cooling(key):
                    self._worker_idx = idx
                    return key
            
            raise AllWorkerKeysCoolingDown(
                f"All {n} enrichment worker key(s) are in cooldown."
            )

    def worker_pool_status(self) -> dict:
        """Return a diagnostic summary (useful for logging)."""
        with self._lock:
            now = time.monotonic()
            keys = self._worker_keys()
            status = {}
            for i, key in enumerate(keys, 1):
                exp = self._cooldowns.get(key, 0.0)
                remaining = max(0.0, exp - now)
                status[f"worker_{i}"] = {
                    "suffix": f"...{key[-4:]}",
                    "cooling": remaining > 0,
                    "cooldown_remaining_s": round(remaining, 1),
                }
            return status


# ── Module-level singleton ───────────────────────────────────────────────────

groq_pool = _ProviderPool()


def get_search_key():
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
    except ImportError:
        pass
    return os.getenv("GROQ_API_KEY_SEARCH_DEDICATED")

