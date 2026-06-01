from datetime import datetime, timedelta
import csv
import json
import os
import re
import secrets

import runtime_compat
from dotenv import load_dotenv
try:
    from flask_caching import Cache
except ImportError:  # pragma: no cover - fallback keeps app bootable before dependency install
    class Cache:  # type: ignore[override]
        def __init__(self):
            self._store = {}

        def init_app(self, app):
            return None

        def memoize(self, timeout=None):
            def decorator(func):
                return func
            return decorator

        def delete_memoized(self, *args, **kwargs):
            return None

        def get(self, key):
            return self._store.get(key)

        def set(self, key, value, timeout=None):
            self._store[key] = value
            return True

        def delete(self, key):
            self._store.pop(key, None)
            return True

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import LoginManager, current_user, logout_user
from flask_migrate import Migrate
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

from config import BASE_DIR, Config, DatabaseConfig
from app.db_health import get_database_health, print_database_health
from app.models import User, db


load_dotenv()
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "info"
migrate = Migrate()
cache = Cache()
SEARCH_CACHE_TTL_SECONDS = 60  # Dynamic/global cache stays short-lived.
APP_SHELL_START = "<!--app-shell-start-->"
APP_SHELL_END = "<!--app-shell-end-->"


def _bounded_int(env_name, default, minimum, maximum):
    try:
        value = int(os.environ.get(env_name, default))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(value, maximum))


def _db_label(db_config):
    if db_config.db_type == "postgresql":
        provider = f" ({db_config.provider})" if db_config.provider else ""
        return f"PostgreSQL{provider}"
    return "SQLite"


def _print_db_diagnostics(db_config, connection_status=None):
    if db_config.db_type == "postgresql":
        print(f"[DB] Using {_db_label(db_config)}")
        print(f"[DB] Host: {db_config.hostname or 'unknown'}")
    else:
        print("[DB] Using SQLite")
        print("[DB] Host: local file")

    if hasattr(db_config, "warnings"):
        for warning in db_config.warnings:
            print(f"[DB] Warning: {warning}")

    if hasattr(db_config, "fallback_used") and db_config.fallback_used:
        print("[DB] Falling back to SQLite")

    if connection_status:
        print(f"[DB] {connection_status}")



def _database_engine_options(database_uri):
    options = {
        "pool_pre_ping": True,
        "pool_recycle": _bounded_int("SQLALCHEMY_POOL_RECYCLE", 1800, 300, 3600),
    }
    if database_uri.startswith("postgresql"):
        options.update(
            {
                "pool_timeout": _bounded_int("SQLALCHEMY_POOL_TIMEOUT", 30, 5, 30),
                "pool_size": _bounded_int("SQLALCHEMY_POOL_SIZE", 3, 1, 5),
                "max_overflow": _bounded_int("SQLALCHEMY_MAX_OVERFLOW", 2, 0, 5),
                "connect_args": {
                    "connect_timeout": _bounded_int("SQLALCHEMY_CONNECT_TIMEOUT", 10, 3, 30),
                },
            }
        )
    return options


def _verify_startup_connection(database_uri, engine_options, attempts=2):
    last_error = None
    for _ in range(max(1, attempts)):
        engine = create_engine(database_uri, **engine_options)
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True, None
        except SQLAlchemyError as exc:
            last_error = exc
        finally:
            engine.dispose()
    return False, last_error


def _prepare_database_config(app):
    import sys
    db_config = app.config["DB_CONFIG"]
    engine_options = _database_engine_options(db_config.uri)

    # Verify PostgreSQL connectivity
    ok, error = _verify_startup_connection(db_config.uri, engine_options)
    if not ok:
        app.logger.critical(f"CRITICAL DATABASE CONNECTION FAILURE: {error}")
        raise RuntimeError(f"CRITICAL: Failed to connect to primary PostgreSQL database: {error}")

    is_migration_command = (
        len(sys.argv) > 0
        and "flask" in sys.argv[0].lower()
        and any(
            cmd in sys.argv
            for cmd in [
                "db",
                "upgrade",
                "downgrade",
                "migrate",
                "revision",
                "stamp",
                "init"
            ]
        )
    )

    if is_migration_command:
        app.logger.warning("Migration command detected. Skipping strict schema validation.")
        app.config["DATABASE_MODE"] = "postgres_primary"
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = engine_options
        return

    # Verify schema access & check required tables
    try:
        engine = create_engine(db_config.uri, **engine_options)
        with engine.connect() as connection:
            inspector = inspect(engine)
            tables = set(inspector.get_table_names())
            
            # Check if alembic_version exists
            if "alembic_version" not in tables:
                app.logger.warning("Fresh database detected. Skipping strict schema validation until migrations run.")
            else:
                # Check required tables
                required = {
                    "vocabulary_master",
                    "vocabulary_enrichment",
                    "user_word_progress",
                    "user_level_progress",
                    "flashcard_sessions",
                    "flashcard_session_words",
                    "search_history",
                    "vocabulary_review_flags",
                }
                missing = required - tables
                if missing:
                    app.logger.critical(f"CRITICAL DATABASE SCHEMA INSPECTION FAILURE: Missing tables: {missing}")
                    raise RuntimeError(f"CRITICAL: Database schema is incomplete. Missing tables: {missing}")
    except Exception as exc:
        if isinstance(exc, RuntimeError):
            raise exc
        app.logger.critical(f"CRITICAL DATABASE HEALTH VERIFICATION FAILURE: {exc}")
        raise RuntimeError(f"CRITICAL: Database health verification failed: {exc}")

    app.config["DATABASE_MODE"] = "postgres_primary"
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = engine_options
    _print_db_diagnostics(db_config, "Connection and health checks successful")




def _auto_import_vocabulary_if_empty():
    from app.models import VocabularyMaster
    from app.services.vocabulary_platform import is_phrase, normalize_level, normalize_vocab_text

    if VocabularyMaster.query.count() > 0:
        return

    vocab_dir = BASE_DIR / "VWords"
    if not vocab_dir.exists():
        print("[DB] vocabulary_master is empty. Recovery: add CSV files to VWords and run scripts/import_vocabularies.py.")
        return

    imported = 0
    seen = set()
    for path in sorted(vocab_dir.glob("*.csv")):
        with path.open(newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                word = normalize_vocab_text(row.get("word"))
                if not word or word in seen:
                    continue
                seen.add(word)
                filename = path.stem.lower()
                level = normalize_level(row.get("level") or ("advanced" if "advanced" in filename else "upper_intermediate" if "upper" in filename else "intermediate"))
                try:
                    page_no = int(str(row.get("page_no") or "").strip())
                except ValueError:
                    page_no = None
                db.session.add(
                    VocabularyMaster(
                        word=word,
                        normalized_word=word,
                        level=level,
                        page_no=page_no,
                        source_book=path.name,
                        is_phrase=is_phrase(word),
                    )
                )
                imported += 1
    db.session.commit()
    print(f"[DB] vocabulary_master was empty; imported {imported} rows from VWords CSV files.")


def _backfill_legacy_learning_progress():
    from app.models import (
        FlashcardSession,
        FlashcardSessionWord,
        StudySession,
        UserWord,
        UserWordProgress,
        VocabularyMaster,
        Word,
    )
    from app.services.vocabulary_platform import normalize_level, normalize_vocab_text, is_phrase

    inspector = inspect(db.engine)
    tables = set(inspector.get_table_names())
    if not {"word", "user_word", "study_session", "vocabulary_master", "user_word_progress"}.issubset(tables):
        return

    created_progress = 0
    for legacy_progress in UserWord.query.all():
        legacy_word = db.session.get(Word, legacy_progress.word_id)
        if legacy_word is None:
            continue
        normalized = normalize_vocab_text(legacy_word.word)
        if not normalized:
            continue
        vocabulary = VocabularyMaster.query.filter_by(normalized_word=normalized).first()
        if vocabulary is None:
            vocabulary = VocabularyMaster(
                word=normalized,
                normalized_word=normalized,
                level=normalize_level(legacy_word.difficulty or "intermediate"),
                source_book="legacy_word_table",
                is_phrase=is_phrase(normalized),
            )
            db.session.add(vocabulary)
            db.session.flush()
        progress = UserWordProgress.query.filter_by(
            user_id=legacy_progress.user_id,
            vocabulary_id=vocabulary.id,
        ).first()
        if progress is None:
            progress = UserWordProgress(
                user_id=legacy_progress.user_id,
                vocabulary_id=vocabulary.id,
                is_generated=True,
                is_learned=bool(legacy_progress.learned or legacy_progress.already_known),
                is_difficult=bool(legacy_progress.is_difficult),
                is_favorite=bool(legacy_progress.is_favorite),
                times_seen=1,
                times_reviewed=1 if legacy_progress.last_reviewed else 0,
                last_seen_at=datetime.combine(legacy_progress.added_date, datetime.min.time()) if legacy_progress.added_date else None,
                last_reviewed_at=datetime.combine(legacy_progress.last_reviewed, datetime.min.time()) if legacy_progress.last_reviewed else None,
            )
            db.session.add(progress)
            created_progress += 1

    existing_legacy_session_ids = {
        int(item.order_mode.replace("legacy:", ""))
        for item in FlashcardSession.query.filter(FlashcardSession.order_mode.like("legacy:%")).all()
        if item.order_mode and item.order_mode.replace("legacy:", "").isdigit()
    }
    created_sessions = 0
    for legacy_session in StudySession.query.all():
        if legacy_session.id in existing_legacy_session_ids:
            continue
        legacy_words = UserWord.query.filter_by(session_id=legacy_session.id).all()
        if not legacy_words:
            continue
        session = FlashcardSession(
            user_id=legacy_session.user_id,
            level=normalize_level(legacy_session.difficulty),
            requested_count=legacy_session.word_count or len(legacy_words),
            generated_count=len(legacy_words),
            order_mode=f"legacy:{legacy_session.id}",
            created_at=datetime.combine(legacy_session.created_at, datetime.min.time()) if legacy_session.created_at else datetime.utcnow(),
        )
        db.session.add(session)
        db.session.flush()
        created_sessions += 1
        seen_session_vocab_ids = set()
        for position, legacy_progress in enumerate(legacy_words, start=1):
            legacy_word = db.session.get(Word, legacy_progress.word_id)
            if legacy_word is None:
                continue
            vocabulary = VocabularyMaster.query.filter_by(normalized_word=normalize_vocab_text(legacy_word.word)).first()
            if vocabulary is not None and vocabulary.id not in seen_session_vocab_ids:
                seen_session_vocab_ids.add(vocabulary.id)
                db.session.add(FlashcardSessionWord(session_id=session.id, vocabulary_id=vocabulary.id, position=position))

    if created_progress or created_sessions:
        db.session.commit()
        print(f"[DB] Restored {created_progress} legacy progress rows and {created_sessions} legacy sessions.")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def ensure_column(table_name, column_name, ddl):
    inspector = inspect(db.engine)
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    if column_name not in columns:
        db.session.execute(text(ddl))
        db.session.commit()


def ensure_index(index_name, ddl):
    inspector = inspect(db.engine)
    existing_indexes = {index["name"] for table_name in inspector.get_table_names() for index in inspector.get_indexes(table_name)}
    if index_name not in existing_indexes:
        db.session.execute(text(ddl))
        db.session.commit()


def run_migrations():
    """Keep SQLite schemas compatible without requiring Alembic."""
    ensure_column("word", "is_valid", "ALTER TABLE word ADD COLUMN is_valid BOOLEAN DEFAULT TRUE")
    ensure_column("word", "bangla_meaning", "ALTER TABLE word ADD COLUMN bangla_meaning TEXT")
    ensure_column("word", "difficulty", "ALTER TABLE word ADD COLUMN difficulty VARCHAR(20)")
    ensure_column("word", "part_of_speech", "ALTER TABLE word ADD COLUMN part_of_speech VARCHAR(50)")
    ensure_column("word", "bangla_pronunciation", "ALTER TABLE word ADD COLUMN bangla_pronunciation TEXT")
    ensure_column("word", "phonetic", "ALTER TABLE word ADD COLUMN phonetic TEXT")
    ensure_column("word", "synonym", "ALTER TABLE word ADD COLUMN synonym TEXT")
    ensure_column("word", "memory_trick", "ALTER TABLE word ADD COLUMN memory_trick TEXT")
    ensure_column("word", "topic", "ALTER TABLE word ADD COLUMN topic VARCHAR(120)")
    ensure_column("word", "created_at", "ALTER TABLE word ADD COLUMN created_at DATE")
    ensure_column("user_word", "session_id", "ALTER TABLE user_word ADD COLUMN session_id INTEGER")
    ensure_column("user_word", "already_known", "ALTER TABLE user_word ADD COLUMN already_known BOOLEAN DEFAULT FALSE")
    ensure_column("user_word", "is_difficult", "ALTER TABLE user_word ADD COLUMN is_difficult BOOLEAN DEFAULT FALSE")
    ensure_column("user_word", "is_favorite", "ALTER TABLE user_word ADD COLUMN is_favorite BOOLEAN DEFAULT FALSE")
    ensure_column("user_word", "note", "ALTER TABLE user_word ADD COLUMN note TEXT")
    ensure_column("user_word", "learned_at", "ALTER TABLE user_word ADD COLUMN learned_at DATE")
    ensure_column("study_session", "custom_prompt", "ALTER TABLE study_session ADD COLUMN custom_prompt TEXT")
    ensure_column("user", "default_study_focus", "ALTER TABLE user ADD COLUMN default_study_focus TEXT")
    ensure_column("user", "daily_goal", "ALTER TABLE user ADD COLUMN daily_goal INTEGER DEFAULT 10")
    ensure_column("user", "nickname", "ALTER TABLE user ADD COLUMN nickname VARCHAR(80)")
    ensure_column("user", "created_at", "ALTER TABLE user ADD COLUMN created_at DATE")
    ensure_column("user", "last_login_at", "ALTER TABLE user ADD COLUMN last_login_at DATETIME")
    ensure_column("user", "is_restricted", "ALTER TABLE user ADD COLUMN is_restricted BOOLEAN DEFAULT FALSE")
    ensure_column("user", "restricted_reason", "ALTER TABLE user ADD COLUMN restricted_reason TEXT")
    ensure_column("vocabulary_master", "needs_admin_review", "ALTER TABLE vocabulary_master ADD COLUMN needs_admin_review BOOLEAN DEFAULT FALSE")
    ensure_column("vocabulary_master", "review_reason", "ALTER TABLE vocabulary_master ADD COLUMN review_reason TEXT")
    ensure_column("vocabulary_master", "original_word", "ALTER TABLE vocabulary_master ADD COLUMN original_word VARCHAR(180)")
    ensure_column("vocabulary_master", "corrected_at", "ALTER TABLE vocabulary_master ADD COLUMN corrected_at DATETIME")
    ensure_column("vocabulary_master", "corrected_by_admin", "ALTER TABLE vocabulary_master ADD COLUMN corrected_by_admin BOOLEAN DEFAULT FALSE")
    ensure_column("vocabulary_master", "last_audited_at", "ALTER TABLE vocabulary_master ADD COLUMN last_audited_at DATETIME")
    ensure_column("vocabulary_enrichment", "last_audited_at", "ALTER TABLE vocabulary_enrichment ADD COLUMN last_audited_at DATETIME")
    ensure_column("vocabulary_enrichment", "last_regenerated_at", "ALTER TABLE vocabulary_enrichment ADD COLUMN last_regenerated_at DATETIME")
    ensure_column("vocabulary_enrichment", "validation_status", "ALTER TABLE vocabulary_enrichment ADD COLUMN validation_status VARCHAR(50)")
    ensure_column("vocabulary_enrichment", "generation_timestamp", "ALTER TABLE vocabulary_enrichment ADD COLUMN generation_timestamp DATETIME")
    ensure_column("quiz_history", "answered_questions", "ALTER TABLE quiz_history ADD COLUMN answered_questions INTEGER DEFAULT 0")
    ensure_column("quiz_history", "configured_total_questions", "ALTER TABLE quiz_history ADD COLUMN configured_total_questions INTEGER DEFAULT 0")
    ensure_column("quiz_history", "was_quit", "ALTER TABLE quiz_history ADD COLUMN was_quit BOOLEAN DEFAULT FALSE")
    ensure_column("quiz_history", "mistakes_json", "ALTER TABLE quiz_history ADD COLUMN mistakes_json TEXT")
    ensure_column("quiz_history", "weak_vocabulary_ids", "ALTER TABLE quiz_history ADD COLUMN weak_vocabulary_ids TEXT")
    ensure_column("quiz_history", "completion_seconds", "ALTER TABLE quiz_history ADD COLUMN completion_seconds INTEGER DEFAULT 0")
    ensure_column("quiz_history", "retry_of_quiz_id", "ALTER TABLE quiz_history ADD COLUMN retry_of_quiz_id INTEGER")
    ensure_index("ix_word_difficulty", "CREATE INDEX IF NOT EXISTS ix_word_difficulty ON word (difficulty)")
    ensure_index("ix_word_is_valid", "CREATE INDEX IF NOT EXISTS ix_word_is_valid ON word (is_valid)")
    ensure_index("ix_word_topic", "CREATE INDEX IF NOT EXISTS ix_word_topic ON word (topic)")
    ensure_index("ix_study_session_user_created", "CREATE INDEX IF NOT EXISTS ix_study_session_user_created ON study_session (user_id, created_at)")
    ensure_index("ix_quiz_history_user_created", "CREATE INDEX IF NOT EXISTS ix_quiz_history_user_created ON quiz_history (user_id, created_at)")
    ensure_index("ix_user_app_session_user_visit_date", "CREATE INDEX IF NOT EXISTS ix_user_app_session_user_visit_date ON user_app_session (user_id, visit_date)")
    ensure_index("ix_user_app_session_user_last_active", "CREATE INDEX IF NOT EXISTS ix_user_app_session_user_last_active ON user_app_session (user_id, last_active_at)")
    ensure_index("ix_user_word_word_id", "CREATE INDEX IF NOT EXISTS ix_user_word_word_id ON user_word (word_id)")
    ensure_index("ix_user_word_user_added_date", "CREATE INDEX IF NOT EXISTS ix_user_word_user_added_date ON user_word (user_id, added_date)")
    ensure_index("ix_user_word_user_session_learned", "CREATE INDEX IF NOT EXISTS ix_user_word_user_session_learned ON user_word (user_id, session_id, learned)")
    ensure_index("ix_user_word_user_learning_state", "CREATE INDEX IF NOT EXISTS ix_user_word_user_learning_state ON user_word (user_id, learned, already_known)")
    ensure_index("ix_user_word_user_difficult", "CREATE INDEX IF NOT EXISTS ix_user_word_user_difficult ON user_word (user_id, is_difficult)")
    ensure_index("ix_user_word_user_favorite", "CREATE INDEX IF NOT EXISTS ix_user_word_user_favorite ON user_word (user_id, is_favorite)")
    ensure_index("ix_user_word_user_learned_at", "CREATE INDEX IF NOT EXISTS ix_user_word_user_learned_at ON user_word (user_id, learned_at)")
    ensure_index("ix_user_word_user_last_reviewed", "CREATE INDEX IF NOT EXISTS ix_user_word_user_last_reviewed ON user_word (user_id, last_reviewed)")
    ensure_index("ix_user_word_user_rev1", "CREATE INDEX IF NOT EXISTS ix_user_word_user_rev1 ON user_word (user_id, rev1)")
    ensure_index("ix_user_word_user_rev2", "CREATE INDEX IF NOT EXISTS ix_user_word_user_rev2 ON user_word (user_id, rev2)")
    ensure_index("ix_user_word_user_rev3", "CREATE INDEX IF NOT EXISTS ix_user_word_user_rev3 ON user_word (user_id, rev3)")
    ensure_index("ix_vocabulary_master_needs_admin_review", "CREATE INDEX IF NOT EXISTS ix_vocabulary_master_needs_admin_review ON vocabulary_master (needs_admin_review)")
    ensure_index("ix_vocabulary_master_last_audited", "CREATE INDEX IF NOT EXISTS ix_vocabulary_master_last_audited ON vocabulary_master (last_audited_at)")


def cleanup_invalid_words():
    db.session.execute(text("DELETE FROM word WHERE is_valid = FALSE OR length(word) <= 2"))
    db.session.commit()


def create_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
        instance_path=str(BASE_DIR),
    )
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(16)
    _prepare_database_config(app)
    app.config["CACHE_TYPE"] = os.environ.get("CACHE_TYPE", "SimpleCache")
    app.config["CACHE_DEFAULT_TIMEOUT"] = _bounded_int("CACHE_DEFAULT_TIMEOUT", SEARCH_CACHE_TTL_SECONDS, 30, 120)
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = int(os.environ.get("SEND_FILE_MAX_AGE_DEFAULT", "3600"))
    if os.environ.get("TEMPLATES_AUTO_RELOAD", "").lower() in {"1", "true", "yes"}:
        app.config["TEMPLATES_AUTO_RELOAD"] = True
    local_dev = os.environ.get("VFLASH_LOCAL_DEV", "").lower() in {"1", "true", "yes"}
    if local_dev:
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
        app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["DB_FALLBACK_ACTIVE"] = False
    app.config["DB_PRODUCTION_FALLBACK_BLOCKED"] = False
    app.config["ADMIN_EMAIL"] = (os.environ.get("ADMIN_EMAIL") or "").strip().lower()
    app.config["ADMIN_PASSWORD"] = os.environ.get("ADMIN_PASSWORD") or ""
    app.config["ADMIN_PASSWORD_HASH"] = os.environ.get("ADMIN_PASSWORD_HASH") or ""
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["REMEMBER_COOKIE_HTTPONLY"] = True
    app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"
    app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=_bounded_int("REMEMBER_COOKIE_DAYS", 365, 7, 365))
    app.config["REMEMBER_COOKIE_REFRESH_EACH_REQUEST"] = True
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "").lower() in {"1", "true", "yes"}
    app.config["REMEMBER_COOKIE_SECURE"] = app.config["SESSION_COOKIE_SECURE"]

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cache.init_app(app)

    from app.routes import admin, auth, dashboard, flashcards, generate, quiz, review, words

    for module in (auth, dashboard, flashcards, generate, review, quiz, words, admin):
        module.register(app)

    @app.context_processor
    def inject_static_asset_helper():
        def static_asset(filename):
            values = {}
            if local_dev or app.debug:
                static_path = BASE_DIR / "static" / filename
                try:
                    values["v"] = int(static_path.stat().st_mtime)
                except OSError:
                    values["v"] = "dev"
            return url_for("static", filename=filename, **values)

        return {"static_asset": static_asset}

    @app.context_processor
    def inject_database_state():
        return {
            "db_fallback_active": False,
            "db_production_fallback_blocked": False,
            "active_db_type": "postgresql",
        }

    @app.before_request
    def maintenance_mode():
       if (
        os.getenv("MAINTENANCE_MODE", "").lower() in {"1", "true", "yes"}
        and not (current_user.is_authenticated and current_user.email == app.config["ADMIN_EMAIL"])
     ):
        return (
            render_template(
                "error.html",
                error_code=503,
                error_title="🚧 Under Maintenance",
                error_message="We are improving the system. Please come back later.",
            ),
            503,
        )

    @app.before_request
    def enforce_restrictions():
        if not current_user.is_authenticated:
            return None

        if current_user.is_restricted and request.endpoint not in {"login", "logout"}:
            logout_user()
            session.clear()
            flash("Your account has been restricted. Contact the administrator.", "error")
            return redirect(url_for("login"))
        return None

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(error):
        app.logger.exception("Database error occurred during request execution")
        db.session.rollback()
        return render_template(
            "error.html",
            error_code=500,
            error_title="Something went wrong",
            error_message="A database error occurred. We are preparing a safe recovery path. Please return to your dashboard and continue from there.",
        ), 500

    @app.after_request
    def apply_security_headers(response):
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data:; "
            "media-src 'self' data: blob:; "
            "connect-src 'self'; "
            "frame-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        if request.endpoint == "static" and response.status_code == 200:
            if local_dev or app.debug:
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
            else:
                response.headers["Cache-Control"] = f"public, max-age={app.get_send_file_max_age(None) or 3600}"
        elif response.mimetype == "text/html" and response.status_code == 200:
            response.headers["Cache-Control"] = "private, no-cache, must-revalidate"
        if request.endpoint and request.endpoint.startswith("admin"):
            response.headers["Cache-Control"] = "no-store"
        if (
            request.headers.get("X-App-Fragment") == "1"
            and response.mimetype == "text/html"
            and response.status_code == 200
        ):
            html = response.get_data(as_text=True)
            shell = ""
            if APP_SHELL_START in html and APP_SHELL_END in html:
                shell = html.split(APP_SHELL_START, 1)[1].split(APP_SHELL_END, 1)[0].strip()

            title_match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
            title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else ""
            payload = {
                "ok": True,
                "title": title,
                "path": request.full_path if request.query_string else request.path,
                "shell": shell,
            }
            response = app.response_class(
                response=json.dumps(payload),
                status=response.status_code,
                mimetype="application/json",
            )
            response.headers["Cache-Control"] = "private, no-cache, must-revalidate"
        return response

    @app.get("/health")
    def health():
        health_info = get_database_health(app)
        status_code = 200 if health_info["status"] == "ok" else 503
        return {"status": health_info["status"], "database": health_info}, status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        return (
            render_template(
                "error.html",
                error_code=404,
                error_title="Page not found",
                error_message="The page you are looking for is not available.",
            ),
            404,
        )

    @app.errorhandler(500)
    def handle_server_error(error):
        db.session.rollback()
        return (
            render_template(
                "error.html",
                error_code=500,
                error_title="Something went wrong",
                error_message="We are preparing a safe recovery path. Please return to your dashboard and continue from there.",
            ),
            500,
        )

    auto_bootstrap_db = os.environ.get("AUTO_BOOTSTRAP_DB", "1").lower() in {"1", "true", "yes"}

    with app.app_context():
        if auto_bootstrap_db:
            _backfill_legacy_learning_progress()
        app.config["DB_HEALTH"] = print_database_health(app)

        # Start continuous background cache saturation safely
        from app.services.vocabulary_platform import start_continuous_enrichment_worker
        start_continuous_enrichment_worker(app)

    return app
