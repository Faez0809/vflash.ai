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
    vocabulary_progress = db.relationship(
        "UserWordProgress",
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


class VocabularyMaster(db.Model):
    __tablename__ = "vocabulary_master"
    __table_args__ = (
        Index("ix_vocabulary_master_normalized_word", "normalized_word"),
        Index("ix_vocabulary_master_level", "level"),
    )

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(180), nullable=False)
    normalized_word = db.Column(db.String(180), unique=True, nullable=False)
    level = db.Column(db.String(40), nullable=False)
    page_no = db.Column(db.Integer, nullable=True)
    source_book = db.Column(db.String(120), nullable=True)
    is_phrase = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    needs_admin_review = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    review_reason = db.Column(db.Text, nullable=True)
    original_word = db.Column(db.String(180), nullable=True)
    corrected_at = db.Column(db.DateTime, nullable=True)
    corrected_by_admin = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    last_audited_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    enrichment = db.relationship(
        "VocabularyEnrichment",
        back_populates="vocabulary",
        uselist=False,
        cascade="all, delete-orphan",
    )
    review_flags = db.relationship(
        "VocabularyReviewFlag",
        back_populates="vocabulary",
        cascade="all, delete-orphan",
    )
    user_progress = db.relationship(
        "UserWordProgress",
        back_populates="vocabulary",
        cascade="all, delete-orphan",
    )


class VocabularyReviewFlag(db.Model):
    __tablename__ = "vocabulary_review_flags"
    __table_args__ = (
        Index("ix_vocabulary_review_flags_status", "status"),
        Index("ix_vocabulary_review_flags_flag_type", "flag_type"),
        Index("ix_vocabulary_review_flags_vocabulary_id", "vocabulary_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    vocabulary_id = db.Column(db.Integer, db.ForeignKey("vocabulary_master.id"), nullable=True)
    original_word = db.Column(db.String(180), nullable=False)
    corrected_word = db.Column(db.String(180), nullable=True)
    flag_type = db.Column(db.String(60), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="pending", server_default="pending")
    level = db.Column(db.String(40), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    vocabulary = db.relationship("VocabularyMaster", back_populates="review_flags")


class VocabularyEnrichment(db.Model):
    __tablename__ = "vocabulary_enrichment"
    __table_args__ = (
        Index("ix_vocabulary_enrichment_vocabulary_id", "vocabulary_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    vocabulary_id = db.Column(db.Integer, db.ForeignKey("vocabulary_master.id"), unique=True, nullable=False)
    definition = db.Column(db.Text, nullable=False)
    bangla_meaning = db.Column(db.Text, nullable=True)
    pronunciation = db.Column(db.Text, nullable=True)
    synonyms = db.Column(db.Text, nullable=True)
    antonyms = db.Column(db.Text, nullable=True)
    example_sentence = db.Column(db.Text, nullable=True)
    memory_tip = db.Column(db.Text, nullable=True)
    part_of_speech = db.Column(db.String(80), nullable=True)
    quality_verified = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    enrichment_quality_score = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    audit_flags = db.Column(db.Text, nullable=True)
    generated_by_model = db.Column(db.String(120), nullable=True)
    corrected_manually = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_audited_at = db.Column(db.DateTime, nullable=True)
    last_regenerated_at = db.Column(db.DateTime, nullable=True)

    vocabulary = db.relationship("VocabularyMaster", back_populates="enrichment")


class UserWordProgress(db.Model):
    __tablename__ = "user_word_progress"
    __table_args__ = (
        db.UniqueConstraint("user_id", "vocabulary_id", name="uq_user_word_progress_user_vocabulary"),
        Index("ix_user_word_progress_user_id", "user_id"),
        Index("ix_user_word_progress_vocabulary_id", "vocabulary_id"),
        Index("ix_user_word_progress_user_generated", "user_id", "is_generated"),
        Index("ix_user_word_progress_user_learned", "user_id", "is_learned"),
        Index("ix_user_word_progress_user_difficult", "user_id", "is_difficult"),
        Index("ix_user_word_progress_user_reviewed", "user_id", "is_reviewed"),
        Index("ix_user_word_progress_user_favorite", "user_id", "is_favorite"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    vocabulary_id = db.Column(db.Integer, db.ForeignKey("vocabulary_master.id"), nullable=False)
    is_generated = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    is_learned = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    is_difficult = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    is_reviewed = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    is_favorite = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    times_seen = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    times_reviewed = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    last_seen_at = db.Column(db.DateTime, nullable=True)
    last_reviewed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="vocabulary_progress")
    vocabulary = db.relationship("VocabularyMaster", back_populates="user_progress")

    @property
    def word_entry(self):
        return VocabularyCardProxy(self.vocabulary)

    @property
    def learned(self):
        return self.is_learned

    @learned.setter
    def learned(self, value):
        self.is_learned = bool(value)

    @property
    def already_known(self):
        return False

    @already_known.setter
    def already_known(self, value):
        if value:
            self.is_learned = True

    @property
    def note(self):
        return None


class UserLevelProgress(db.Model):
    __tablename__ = "user_level_progress"
    __table_args__ = (
        db.UniqueConstraint("user_id", "level", name="uq_user_level_progress_user_level"),
        Index("ix_user_level_progress_user_id", "user_id"),
        Index("ix_user_level_progress_level", "level"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    level = db.Column(db.String(40), nullable=False)
    last_alphabetical_word_id = db.Column(db.Integer, db.ForeignKey("vocabulary_master.id"), nullable=True)
    completed_percentage = db.Column(db.Float, nullable=False, default=0.0, server_default="0")
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User")
    last_alphabetical_word = db.relationship("VocabularyMaster")


class SearchHistory(db.Model):
    __tablename__ = "search_history"
    __table_args__ = (
        Index("ix_search_history_user_id", "user_id"),
        Index("ix_search_history_matched_vocabulary_id", "matched_vocabulary_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    search_query = db.Column(db.String(180), nullable=False)
    matched_vocabulary_id = db.Column(db.Integer, db.ForeignKey("vocabulary_master.id"), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User")
    matched_vocabulary = db.relationship("VocabularyMaster")


class FlashcardSession(db.Model):
    __tablename__ = "flashcard_sessions"
    __table_args__ = (
        Index("ix_flashcard_sessions_user_id", "user_id"),
        Index("ix_flashcard_sessions_user_created", "user_id", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    level = db.Column(db.String(40), nullable=False)
    requested_count = db.Column(db.Integer, nullable=False)
    generated_count = db.Column(db.Integer, nullable=False)
    order_mode = db.Column(db.String(20), nullable=False, default="alphabetical")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User")
    session_words = db.relationship(
        "FlashcardSessionWord",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="FlashcardSessionWord.position",
    )

    @property
    def difficulty(self):
        return self.level

    @property
    def word_count(self):
        return self.generated_count

    @property
    def custom_prompt(self):
        return self.order_mode


class FlashcardSessionWord(db.Model):
    __tablename__ = "flashcard_session_words"
    __table_args__ = (
        db.UniqueConstraint("session_id", "vocabulary_id", name="uq_flashcard_session_word"),
        Index("ix_flashcard_session_words_session_id", "session_id"),
        Index("ix_flashcard_session_words_vocabulary_id", "vocabulary_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("flashcard_sessions.id"), nullable=False)
    vocabulary_id = db.Column(db.Integer, db.ForeignKey("vocabulary_master.id"), nullable=False)
    position = db.Column(db.Integer, nullable=False)

    session = db.relationship("FlashcardSession", back_populates="session_words")
    vocabulary = db.relationship("VocabularyMaster")


class SearchVocabulary(db.Model):
    __tablename__ = "search_vocabulary"
    __table_args__ = (
        Index("ix_search_vocabulary_normalized_word", "normalized_word"),
        Index("ix_search_vocabulary_searched_by_user_id", "searched_by_user_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(180), nullable=False)
    normalized_word = db.Column(db.String(180), unique=True, nullable=False)
    searched_by_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    definition = db.Column(db.Text, nullable=True)
    bangla_meaning = db.Column(db.Text, nullable=True)
    pronunciation = db.Column(db.Text, nullable=True)
    synonyms = db.Column(db.Text, nullable=True)
    antonyms = db.Column(db.Text, nullable=True)
    example_sentence = db.Column(db.Text, nullable=True)
    part_of_speech = db.Column(db.String(80), nullable=True)
    difficulty_estimate = db.Column(db.String(40), nullable=True)
    source_type = db.Column(db.String(40), nullable=False, default="search")
    ai_generated = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    searched_by_user = db.relationship("User")

    @property
    def meaning(self):
        return self.definition

    @property
    def phonetic(self):
        return self.pronunciation

    @property
    def synonym(self):
        return self.synonyms

    @property
    def synonym_hint(self):
        return self.synonyms

    @property
    def antonym_hint(self):
        return self.antonyms

    @property
    def sentence(self):
        return self.example_sentence

    @property
    def memory_trick(self):
        return None

    @property
    def lookup_pending(self):
        return not bool(self.definition)


class LegacySavedNote(db.Model):
    __tablename__ = "legacy_saved_notes"
    __table_args__ = (
        Index("ix_legacy_saved_notes_user_id", "user_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    word = db.Column(db.String(180), nullable=False)
    note = db.Column(db.Text, nullable=False)
    archived_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User")


class VocabularyCardProxy:
    def __init__(self, vocabulary):
        self._vocabulary = vocabulary
        self._enrichment = vocabulary.enrichment if vocabulary else None

    @property
    def id(self):
        return self._vocabulary.id

    @property
    def word(self):
        return self._vocabulary.word

    @property
    def normalized_word(self):
        return self._vocabulary.normalized_word

    @property
    def difficulty(self):
        return self._vocabulary.level

    @property
    def topic(self):
        return self._vocabulary.source_book or self._vocabulary.level

    @property
    def meaning(self):
        return self._enrichment.definition if self._enrichment else "Definition is being prepared."

    @property
    def bangla_meaning(self):
        return self._enrichment.bangla_meaning if self._enrichment else None

    @property
    def phonetic(self):
        return self._enrichment.pronunciation if self._enrichment else None

    @property
    def synonym(self):
        return self._enrichment.synonyms if self._enrichment else None

    @property
    def synonym_hint(self):
        return self.synonym

    @property
    def antonym_hint(self):
        return self._enrichment.antonyms if self._enrichment else None

    @property
    def memory_trick(self):
        return self._enrichment.memory_tip if self._enrichment else None

    @property
    def sentence(self):
        return self._enrichment.example_sentence if self._enrichment else None

    @property
    def part_of_speech(self):
        return self._enrichment.part_of_speech if self._enrichment else None


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(120), unique=True, nullable=False)
    is_valid = db.Column(db.Boolean, nullable=False, default=True, index=True)
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
    mistakes_json = db.Column(db.Text, nullable=True)
    weak_vocabulary_ids = db.Column(db.Text, nullable=True)
    completion_seconds = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    retry_of_quiz_id = db.Column(db.Integer, nullable=True)
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
