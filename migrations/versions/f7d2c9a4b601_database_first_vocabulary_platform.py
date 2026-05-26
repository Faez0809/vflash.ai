"""database first vocabulary platform

Revision ID: f7d2c9a4b601
Revises: e6f9b7d4c2a1
Create Date: 2026-05-25 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "f7d2c9a4b601"
down_revision = "e6f9b7d4c2a1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "vocabulary_master",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("word", sa.String(length=180), nullable=False),
        sa.Column("normalized_word", sa.String(length=180), nullable=False),
        sa.Column("level", sa.String(length=40), nullable=False),
        sa.Column("page_no", sa.Integer(), nullable=True),
        sa.Column("source_book", sa.String(length=120), nullable=True),
        sa.Column("is_phrase", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("normalized_word"),
    )
    op.create_index("ix_vocabulary_master_normalized_word", "vocabulary_master", ["normalized_word"])
    op.create_index("ix_vocabulary_master_level", "vocabulary_master", ["level"])

    op.create_table(
        "vocabulary_enrichment",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("vocabulary_id", sa.Integer(), nullable=False),
        sa.Column("definition", sa.Text(), nullable=False),
        sa.Column("bangla_meaning", sa.Text(), nullable=True),
        sa.Column("pronunciation", sa.Text(), nullable=True),
        sa.Column("synonyms", sa.Text(), nullable=True),
        sa.Column("antonyms", sa.Text(), nullable=True),
        sa.Column("example_sentence", sa.Text(), nullable=True),
        sa.Column("memory_tip", sa.Text(), nullable=True),
        sa.Column("part_of_speech", sa.String(length=80), nullable=True),
        sa.Column("quality_verified", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("generated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["vocabulary_id"], ["vocabulary_master.id"]),
        sa.UniqueConstraint("vocabulary_id"),
    )
    op.create_index("ix_vocabulary_enrichment_vocabulary_id", "vocabulary_enrichment", ["vocabulary_id"])

    op.create_table(
        "user_word_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("vocabulary_id", sa.Integer(), nullable=False),
        sa.Column("is_generated", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_learned", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_difficult", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_reviewed", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_favorite", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("times_seen", sa.Integer(), server_default="0", nullable=False),
        sa.Column("times_reviewed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_seen_at", sa.DateTime(), nullable=True),
        sa.Column("last_reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["vocabulary_id"], ["vocabulary_master.id"]),
        sa.UniqueConstraint("user_id", "vocabulary_id", name="uq_user_word_progress_user_vocabulary"),
    )
    op.create_index("ix_user_word_progress_user_id", "user_word_progress", ["user_id"])
    op.create_index("ix_user_word_progress_vocabulary_id", "user_word_progress", ["vocabulary_id"])
    op.create_index("ix_user_word_progress_user_generated", "user_word_progress", ["user_id", "is_generated"])
    op.create_index("ix_user_word_progress_user_learned", "user_word_progress", ["user_id", "is_learned"])
    op.create_index("ix_user_word_progress_user_difficult", "user_word_progress", ["user_id", "is_difficult"])
    op.create_index("ix_user_word_progress_user_reviewed", "user_word_progress", ["user_id", "is_reviewed"])
    op.create_index("ix_user_word_progress_user_favorite", "user_word_progress", ["user_id", "is_favorite"])

    op.create_table(
        "search_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("search_query", sa.String(length=180), nullable=False),
        sa.Column("matched_vocabulary_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["matched_vocabulary_id"], ["vocabulary_master.id"]),
    )
    op.create_index("ix_search_history_user_id", "search_history", ["user_id"])
    op.create_index("ix_search_history_matched_vocabulary_id", "search_history", ["matched_vocabulary_id"])

    op.create_table(
        "flashcard_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("level", sa.String(length=40), nullable=False),
        sa.Column("requested_count", sa.Integer(), nullable=False),
        sa.Column("generated_count", sa.Integer(), nullable=False),
        sa.Column("order_mode", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
    )
    op.create_index("ix_flashcard_sessions_user_id", "flashcard_sessions", ["user_id"])
    op.create_index("ix_flashcard_sessions_user_created", "flashcard_sessions", ["user_id", "created_at"])

    op.create_table(
        "flashcard_session_words",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("vocabulary_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["flashcard_sessions.id"]),
        sa.ForeignKeyConstraint(["vocabulary_id"], ["vocabulary_master.id"]),
        sa.UniqueConstraint("session_id", "vocabulary_id", name="uq_flashcard_session_word"),
    )
    op.create_index("ix_flashcard_session_words_session_id", "flashcard_session_words", ["session_id"])
    op.create_index("ix_flashcard_session_words_vocabulary_id", "flashcard_session_words", ["vocabulary_id"])

    op.create_table(
        "search_vocabulary",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("word", sa.String(length=180), nullable=False),
        sa.Column("normalized_word", sa.String(length=180), nullable=False),
        sa.Column("searched_by_user_id", sa.Integer(), nullable=False),
        sa.Column("definition", sa.Text(), nullable=True),
        sa.Column("bangla_meaning", sa.Text(), nullable=True),
        sa.Column("pronunciation", sa.Text(), nullable=True),
        sa.Column("synonyms", sa.Text(), nullable=True),
        sa.Column("antonyms", sa.Text(), nullable=True),
        sa.Column("example_sentence", sa.Text(), nullable=True),
        sa.Column("part_of_speech", sa.String(length=80), nullable=True),
        sa.Column("difficulty_estimate", sa.String(length=40), nullable=True),
        sa.Column("source_type", sa.String(length=40), nullable=False),
        sa.Column("ai_generated", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["searched_by_user_id"], ["user.id"]),
        sa.UniqueConstraint("normalized_word"),
    )
    op.create_index("ix_search_vocabulary_normalized_word", "search_vocabulary", ["normalized_word"])
    op.create_index("ix_search_vocabulary_searched_by_user_id", "search_vocabulary", ["searched_by_user_id"])

    op.create_table(
        "legacy_saved_notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("word", sa.String(length=180), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("archived_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
    )
    op.create_index("ix_legacy_saved_notes_user_id", "legacy_saved_notes", ["user_id"])


def downgrade():
    op.drop_index("ix_legacy_saved_notes_user_id", table_name="legacy_saved_notes")
    op.drop_table("legacy_saved_notes")
    op.drop_index("ix_search_vocabulary_searched_by_user_id", table_name="search_vocabulary")
    op.drop_index("ix_search_vocabulary_normalized_word", table_name="search_vocabulary")
    op.drop_table("search_vocabulary")
    op.drop_index("ix_flashcard_session_words_vocabulary_id", table_name="flashcard_session_words")
    op.drop_index("ix_flashcard_session_words_session_id", table_name="flashcard_session_words")
    op.drop_table("flashcard_session_words")
    op.drop_index("ix_flashcard_sessions_user_created", table_name="flashcard_sessions")
    op.drop_index("ix_flashcard_sessions_user_id", table_name="flashcard_sessions")
    op.drop_table("flashcard_sessions")
    op.drop_index("ix_search_history_matched_vocabulary_id", table_name="search_history")
    op.drop_index("ix_search_history_user_id", table_name="search_history")
    op.drop_table("search_history")
    op.drop_index("ix_user_word_progress_user_favorite", table_name="user_word_progress")
    op.drop_index("ix_user_word_progress_user_reviewed", table_name="user_word_progress")
    op.drop_index("ix_user_word_progress_user_difficult", table_name="user_word_progress")
    op.drop_index("ix_user_word_progress_user_learned", table_name="user_word_progress")
    op.drop_index("ix_user_word_progress_user_generated", table_name="user_word_progress")
    op.drop_index("ix_user_word_progress_vocabulary_id", table_name="user_word_progress")
    op.drop_index("ix_user_word_progress_user_id", table_name="user_word_progress")
    op.drop_table("user_word_progress")
    op.drop_index("ix_vocabulary_enrichment_vocabulary_id", table_name="vocabulary_enrichment")
    op.drop_table("vocabulary_enrichment")
    op.drop_index("ix_vocabulary_master_level", table_name="vocabulary_master")
    op.drop_index("ix_vocabulary_master_normalized_word", table_name="vocabulary_master")
    op.drop_table("vocabulary_master")
