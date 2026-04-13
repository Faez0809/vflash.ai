from datetime import timedelta
from pathlib import Path
import os
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
from sqlalchemy import inspect, text

from app.models import User, db


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
LOCAL_DB_PATH = os.environ.get("SQLITE_DB_PATH", str(INSTANCE_DIR / "vocabai.db"))
INSTANCE_DIR.mkdir(exist_ok=True)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "info"
migrate = Migrate()
cache = Cache()
SEARCH_CACHE_TTL_SECONDS = 60  # Dynamic/global cache stays short-lived.


def _bounded_int(env_name, default, minimum, maximum):
    try:
        value = int(os.environ.get(env_name, default))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(value, maximum))


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
    ensure_column("quiz_history", "answered_questions", "ALTER TABLE quiz_history ADD COLUMN answered_questions INTEGER DEFAULT 0")
    ensure_column("quiz_history", "configured_total_questions", "ALTER TABLE quiz_history ADD COLUMN configured_total_questions INTEGER DEFAULT 0")
    ensure_column("quiz_history", "was_quit", "ALTER TABLE quiz_history ADD COLUMN was_quit BOOLEAN DEFAULT FALSE")
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


def create_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(16)
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or f"sqlite:///{LOCAL_DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": _bounded_int("SQLALCHEMY_POOL_RECYCLE", 1800, 300, 3600),
        "pool_timeout": _bounded_int("SQLALCHEMY_POOL_TIMEOUT", 30, 5, 30),
    }
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"].update(
            {
                "pool_size": _bounded_int("SQLALCHEMY_POOL_SIZE", 3, 1, 5),
                "max_overflow": _bounded_int("SQLALCHEMY_MAX_OVERFLOW", 2, 0, 5),
            }
        )
    app.config["CACHE_TYPE"] = os.environ.get("CACHE_TYPE", "SimpleCache")
    app.config["CACHE_DEFAULT_TIMEOUT"] = _bounded_int("CACHE_DEFAULT_TIMEOUT", SEARCH_CACHE_TTL_SECONDS, 30, 120)
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = int(os.environ.get("SEND_FILE_MAX_AGE_DEFAULT", "3600"))
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

    @app.after_request
    def apply_security_headers(response):
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://embed.tawk.to https://*.tawk.to; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://embed.tawk.to https://*.tawk.to; "
            "font-src 'self' https://fonts.gstatic.com https://embed.tawk.to https://*.tawk.to data:; "
            "img-src 'self' data: https://embed.tawk.to https://*.tawk.to; "
            "media-src 'self' data: blob: https://embed.tawk.to https://*.tawk.to; "
            "connect-src 'self' https://embed.tawk.to https://*.tawk.to wss://*.tawk.to; "
            "frame-src 'self' https://embed.tawk.to https://*.tawk.to; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        if request.endpoint == "static" and response.status_code == 200:
            response.headers["Cache-Control"] = f"public, max-age={app.get_send_file_max_age(None) or 3600}"
        elif response.mimetype == "text/html" and response.status_code == 200:
            response.headers["Cache-Control"] = "private, no-cache, must-revalidate"
        if request.endpoint and request.endpoint.startswith("admin"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/health")
    def health():
        db.session.execute(text("SELECT 1"))
        return {"status": "ok"}, 200

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
        if auto_bootstrap_db and app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite:"):
            db.create_all()
        if auto_bootstrap_db:
            run_migrations()

    return app
