from datetime import date, datetime

import runtime_compat
from flask import current_app
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index


db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(80), nullable=True)
    default_study_focus = db.Column(db.Text, nullable=True)
    daily_goal = db.Column(db.Integer, nullable=False, default=10)
    created_at = db.Column(db.Date, nullable=False, default=date.today)
    last_login_at = db.Column(db.DateTime, nullable=True)
    is_restricted = db.Column(db.Boolean, nullable=False, default=False)
    restricted_reason = db.Column(db.Text, nullable=True)
    study_sessions = db.relationship(
        "StudySession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    user_words = db.relationship(
        "UserWord",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @property
    def display_name(self):
        if self.nickname and self.nickname.strip():
            return self.nickname.strip()
        return self.email.split("@")[0]

    @property
    def is_admin(self):
        admin_email = (current_app.config.get("ADMIN_EMAIL") or "").strip().lower()
        return bool(admin_email) and self.email.strip().lower() == admin_email

    @property
    def is_active(self):
        return not self.is_restricted


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(120), unique=True, nullable=False)
    part_of_speech = db.Column(db.String(50), nullable=True)
    meaning = db.Column(db.Text, nullable=False)
    bangla_meaning = db.Column(db.Text, nullable=True)
    bangla_pronunciation = db.Column(db.Text, nullable=True)
    phonetic = db.Column(db.Text, nullable=True)
    synonym = db.Column(db.Text, nullable=True)
    memory_trick = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(20), nullable=True, index=True)
    topic = db.Column(db.String(120), nullable=True, index=True)
    sentence = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.Date, nullable=True)
    user_words = db.relationship(
        "UserWord",
        back_populates="word_entry",
        cascade="all, delete-orphan",
    )


class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    word_count = db.Column(db.Integer, nullable=False)
    custom_prompt = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.Date, nullable=False)

    user = db.relationship("User", back_populates="study_sessions")
    user_words = db.relationship(
        "UserWord",
        back_populates="study_session",
        cascade="all, delete-orphan",
    )


class MasterWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(120), unique=True, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)


class UserWord(db.Model):
    __table_args__ = (
        db.UniqueConstraint("user_id", "word_id", name="unique_user_word"),
        Index("ix_user_word_user_added_date", "user_id", "added_date"),
        Index("ix_user_word_user_session_learned", "user_id", "session_id", "learned"),
        Index("ix_user_word_user_learning_state", "user_id", "learned", "already_known"),
        Index("ix_user_word_user_difficult", "user_id", "is_difficult"),
        Index("ix_user_word_user_favorite", "user_id", "is_favorite"),
        Index("ix_user_word_user_learned_at", "user_id", "learned_at"),
        Index("ix_user_word_user_last_reviewed", "user_id", "last_reviewed"),
        Index("ix_user_word_user_rev1", "user_id", "rev1"),
        Index("ix_user_word_user_rev2", "user_id", "rev2"),
        Index("ix_user_word_user_rev3", "user_id", "rev3"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey("word.id"), nullable=False, index=True)
    session_id = db.Column(db.Integer, db.ForeignKey("study_session.id"), nullable=True)
    added_date = db.Column(db.Date, nullable=False)
    learned = db.Column(db.Boolean, default=False, nullable=False)
    already_known = db.Column(db.Boolean, default=False, nullable=False)
    is_difficult = db.Column(db.Boolean, default=False, nullable=False)
    is_favorite = db.Column(db.Boolean, default=False, nullable=False)
    note = db.Column(db.Text, nullable=True)
    learned_at = db.Column(db.Date, nullable=True)
    rev1 = db.Column(db.Date, nullable=True)
    rev2 = db.Column(db.Date, nullable=True)
    rev3 = db.Column(db.Date, nullable=True)
    last_reviewed = db.Column(db.Date, nullable=True)

    user = db.relationship("User", back_populates="user_words")
    word_entry = db.relationship("Word", back_populates="user_words")
    study_session = db.relationship("StudySession", back_populates="user_words")


class QuizHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quiz_type = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    answered_questions = db.Column(db.Integer, nullable=False, default=0)
    configured_total_questions = db.Column(db.Integer, nullable=False, default=0)
    was_quit = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.Date, nullable=False)

    user = db.relationship("User")


class UserAppSession(db.Model):
    __table_args__ = (
        db.UniqueConstraint("user_id", "session_key", name="unique_user_app_session"),
        Index("ix_user_app_session_user_visit_date", "user_id", "visit_date"),
        Index("ix_user_app_session_user_last_active", "user_id", "last_active_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    session_key = db.Column(db.String(80), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_active_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    active_seconds = db.Column(db.Integer, nullable=False, default=0)
    page_views = db.Column(db.Integer, nullable=False, default=0)
    interaction_count = db.Column(db.Integer, nullable=False, default=0)
    first_path = db.Column(db.String(255), nullable=True)
    last_path = db.Column(db.String(255), nullable=True)

    user = db.relationship("User")
