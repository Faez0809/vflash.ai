import os
import socket
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


# Load .env before reading environment variables so local development gets the
# same config path as production without extra shell setup.
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SQLITE_URI = "sqlite:///instance/vocabai.db"
POSTGRES_SCHEMES = {"postgres", "postgresql", "postgresql+psycopg", "postgresql+psycopg2"}


@dataclass(frozen=True)
class DatabaseConfig:
    uri: str
    db_type: str
    hostname: str | None = None
    fallback_used: bool = False
    provider: str | None = None
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _normalize_postgres_uri(database_url: str) -> str:
    """Normalize Render/Supabase style Postgres URLs for SQLAlchemy + psycopg."""
    database_url = database_url.strip()

    # Some platforms still expose postgres://, while SQLAlchemy expects the
    # postgresql dialect name.
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # Use the psycopg v3 driver already declared in requirements.txt.
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return database_url


def _clean_database_url(database_url: str) -> str:
    return database_url.strip().strip('"').strip("'")


def _detect_provider(hostname: str | None) -> str | None:
    if not hostname:
        return None
    host = hostname.lower()
    if "supabase" in host:
        return "Supabase"
    if "render" in host:
        return "Render"
    return None


def _sqlite_fallback(reason: str) -> DatabaseConfig:
    return DatabaseConfig(
        uri=DEFAULT_SQLITE_URI,
        db_type="sqlite",
        fallback_used=True,
        warnings=(reason,),
    )


def _validate_database_url(database_url: str) -> DatabaseConfig:
    raw_url = _clean_database_url(database_url)
    if not raw_url:
        return _sqlite_fallback("DATABASE_URL is empty; falling back to SQLite.")

    try:
        parsed = make_url(raw_url)
    except ArgumentError as exc:
        return _sqlite_fallback(f"DATABASE_URL is malformed ({exc}); falling back to SQLite.")

    if parsed.drivername not in POSTGRES_SCHEMES:
        return _sqlite_fallback(
            f"DATABASE_URL uses unsupported scheme '{parsed.drivername}'; falling back to SQLite."
        )

    if not parsed.host:
        return _sqlite_fallback("DATABASE_URL does not include a hostname; falling back to SQLite.")

    try:
        socket.getaddrinfo(parsed.host, parsed.port or 5432)
    except socket.gaierror as exc:
        return _sqlite_fallback(
            f"DATABASE_URL hostname '{parsed.host}' could not be resolved ({exc}); falling back to SQLite."
        )

    normalized_uri = _normalize_postgres_uri(raw_url)
    normalized = make_url(normalized_uri)
    return DatabaseConfig(
        uri=normalized_uri,
        db_type="postgresql",
        hostname=normalized.host,
        provider=_detect_provider(normalized.host),
    )


def get_database_uri() -> str:
    """Resolve the app database URI with a safe SQLite fallback."""
    return get_database_config().uri


def get_database_config() -> DatabaseConfig:
    database_url = os.getenv("DATABASE_URL", "")
    if database_url.strip():
        return _validate_database_url(database_url)

    return _sqlite_fallback("DATABASE_URL is not set; falling back to SQLite.")


class Config:
    DB_CONFIG = get_database_config()
    DATABASE_URL_DETECTED = bool(os.getenv("DATABASE_URL", "").strip())
    SQLALCHEMY_DATABASE_URI = DB_CONFIG.uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
