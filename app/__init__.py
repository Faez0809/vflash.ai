from pathlib import Path
import os
import secrets

import runtime_compat
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
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

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes import auth, dashboard, flashcards, generate, quiz, review, words

    for module in (auth, dashboard, flashcards, generate, review, quiz, words):
        module.register(app)

    with app.app_context():
        db.create_all()
        run_migrations()

    return app
