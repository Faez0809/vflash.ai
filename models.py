from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_words = db.relationship(
        "UserWord",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(120), unique=True, nullable=False)
    meaning = db.Column(db.Text, nullable=False)
    sentence = db.Column(db.Text, nullable=True)
    user_words = db.relationship(
        "UserWord",
        back_populates="word_entry",
        cascade="all, delete-orphan",
    )


class UserWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey("word.id"), nullable=False)
    added_date = db.Column(db.Date, nullable=False)
    learned = db.Column(db.Boolean, default=False, nullable=False)
    rev1 = db.Column(db.Date, nullable=True)
    rev2 = db.Column(db.Date, nullable=True)
    rev3 = db.Column(db.Date, nullable=True)
    last_reviewed = db.Column(db.Date, nullable=True)

    user = db.relationship("User", back_populates="user_words")
    word_entry = db.relationship("Word", back_populates="user_words")
