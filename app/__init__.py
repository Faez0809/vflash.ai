from pathlib import Path
import os
import secrets

import runtime_compat
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import LoginManager, current_user, logout_user
from sqlalchemy import inspect, text

from app.models import User, db


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
LOCAL_DB_PATH = r"C:\vocabai\vocabai.db"
INSTANCE_DIR.mkdir(exist_ok=True)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def ensure_column(table_name, column_name, ddl):
    inspector = inspect(db.engine)
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    if column_name not in columns:
        db.session.execute(text(ddl))
        db.session.commit()


def run_migrations():
    """Keep SQLite schemas compatible without requiring Alembic."""
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
    ensure_column("user_word", "already_known", "ALTER TABLE user_word ADD COLUMN already_known BOOLEAN DEFAULT 0")
    ensure_column("user_word", "is_difficult", "ALTER TABLE user_word ADD COLUMN is_difficult BOOLEAN DEFAULT 0")
    ensure_column("user_word", "is_favorite", "ALTER TABLE user_word ADD COLUMN is_favorite BOOLEAN DEFAULT 0")
    ensure_column("user_word", "note", "ALTER TABLE user_word ADD COLUMN note TEXT")
    ensure_column("user_word", "learned_at", "ALTER TABLE user_word ADD COLUMN learned_at DATE")
    ensure_column("study_session", "custom_prompt", "ALTER TABLE study_session ADD COLUMN custom_prompt TEXT")
    ensure_column("user", "default_study_focus", "ALTER TABLE user ADD COLUMN default_study_focus TEXT")
    ensure_column("user", "daily_goal", "ALTER TABLE user ADD COLUMN daily_goal INTEGER DEFAULT 10")
    ensure_column("user", "nickname", "ALTER TABLE user ADD COLUMN nickname VARCHAR(80)")
    ensure_column("user", "created_at", "ALTER TABLE user ADD COLUMN created_at DATE")
    ensure_column("user", "last_login_at", "ALTER TABLE user ADD COLUMN last_login_at DATETIME")
    ensure_column("user", "is_restricted", "ALTER TABLE user ADD COLUMN is_restricted BOOLEAN DEFAULT 0")
    ensure_column("user", "restricted_reason", "ALTER TABLE user ADD COLUMN restricted_reason TEXT")
    ensure_column("quiz_history", "answered_questions", "ALTER TABLE quiz_history ADD COLUMN answered_questions INTEGER DEFAULT 0")
    ensure_column("quiz_history", "configured_total_questions", "ALTER TABLE quiz_history ADD COLUMN configured_total_questions INTEGER DEFAULT 0")
    ensure_column("quiz_history", "was_quit", "ALTER TABLE quiz_history ADD COLUMN was_quit BOOLEAN DEFAULT 0")


def create_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(16)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{LOCAL_DB_PATH}",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["ADMIN_EMAIL"] = (os.environ.get("ADMIN_EMAIL") or "").strip().lower()
    app.config["ADMIN_PASSWORD"] = os.environ.get("ADMIN_PASSWORD") or ""
    app.config["ADMIN_PASSWORD_HASH"] = os.environ.get("ADMIN_PASSWORD_HASH") or ""
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["REMEMBER_COOKIE_HTTPONLY"] = True
    app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "").lower() in {"1", "true", "yes"}
    app.config["REMEMBER_COOKIE_SECURE"] = app.config["SESSION_COOKIE_SECURE"]

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes import admin, auth, dashboard, flashcards, generate, quiz, review, words

    for module in (auth, dashboard, flashcards, generate, review, quiz, words, admin):
        module.register(app)

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
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https://embed.tawk.to https://*.tawk.to; "
            "connect-src 'self' https://embed.tawk.to https://*.tawk.to wss://*.tawk.to; "
            "frame-src 'self' https://embed.tawk.to https://*.tawk.to; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        if request.endpoint and request.endpoint.startswith("admin"):
            response.headers["Cache-Control"] = "no-store"
        return response

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

    with app.app_context():
        db.create_all()
        run_migrations()

    return app
