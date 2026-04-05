import runtime_compat
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    default_study_focus = db.Column(db.Text, nullable=True)
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
    difficulty = db.Column(db.String(20), nullable=True)
    topic = db.Column(db.String(120), nullable=True)
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
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey("word.id"), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("study_session.id"), nullable=True)
    added_date = db.Column(db.Date, nullable=False)
    learned = db.Column(db.Boolean, default=False, nullable=False)
    rev1 = db.Column(db.Date, nullable=True)
    rev2 = db.Column(db.Date, nullable=True)
    rev3 = db.Column(db.Date, nullable=True)
    last_reviewed = db.Column(db.Date, nullable=True)

    user = db.relationship("User", back_populates="user_words")
    word_entry = db.relationship("Word", back_populates="user_words")
    study_session = db.relationship("StudySession", back_populates="user_words")
