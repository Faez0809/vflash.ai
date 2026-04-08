"""add performance indexes

Revision ID: 9f4b7c2a1d10
Revises: 2e4a1408b7d1
Create Date: 2026-04-09 05:05:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "9f4b7c2a1d10"
down_revision = "2e4a1408b7d1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_word_difficulty", "word", ["difficulty"], unique=False)
    op.create_index("ix_word_topic", "word", ["topic"], unique=False)
    op.create_index("ix_study_session_user_created", "study_session", ["user_id", "created_at"], unique=False)
    op.create_index("ix_quiz_history_user_created", "quiz_history", ["user_id", "created_at"], unique=False)
    op.create_index("ix_user_app_session_user_visit_date", "user_app_session", ["user_id", "visit_date"], unique=False)
    op.create_index("ix_user_app_session_user_last_active", "user_app_session", ["user_id", "last_active_at"], unique=False)
    op.create_index("ix_user_word_word_id", "user_word", ["word_id"], unique=False)
    op.create_index("ix_user_word_user_added_date", "user_word", ["user_id", "added_date"], unique=False)
    op.create_index("ix_user_word_user_session_learned", "user_word", ["user_id", "session_id", "learned"], unique=False)
    op.create_index("ix_user_word_user_learning_state", "user_word", ["user_id", "learned", "already_known"], unique=False)
    op.create_index("ix_user_word_user_difficult", "user_word", ["user_id", "is_difficult"], unique=False)
    op.create_index("ix_user_word_user_favorite", "user_word", ["user_id", "is_favorite"], unique=False)
    op.create_index("ix_user_word_user_learned_at", "user_word", ["user_id", "learned_at"], unique=False)
    op.create_index("ix_user_word_user_last_reviewed", "user_word", ["user_id", "last_reviewed"], unique=False)
    op.create_index("ix_user_word_user_rev1", "user_word", ["user_id", "rev1"], unique=False)
    op.create_index("ix_user_word_user_rev2", "user_word", ["user_id", "rev2"], unique=False)
    op.create_index("ix_user_word_user_rev3", "user_word", ["user_id", "rev3"], unique=False)


def downgrade():
    op.drop_index("ix_user_word_user_rev3", table_name="user_word")
    op.drop_index("ix_user_word_user_rev2", table_name="user_word")
    op.drop_index("ix_user_word_user_rev1", table_name="user_word")
    op.drop_index("ix_user_word_user_last_reviewed", table_name="user_word")
    op.drop_index("ix_user_word_user_learned_at", table_name="user_word")
    op.drop_index("ix_user_word_user_favorite", table_name="user_word")
    op.drop_index("ix_user_word_user_difficult", table_name="user_word")
    op.drop_index("ix_user_word_user_learning_state", table_name="user_word")
    op.drop_index("ix_user_word_user_session_learned", table_name="user_word")
    op.drop_index("ix_user_word_user_added_date", table_name="user_word")
    op.drop_index("ix_user_word_word_id", table_name="user_word")
    op.drop_index("ix_user_app_session_user_last_active", table_name="user_app_session")
    op.drop_index("ix_user_app_session_user_visit_date", table_name="user_app_session")
    op.drop_index("ix_quiz_history_user_created", table_name="quiz_history")
    op.drop_index("ix_study_session_user_created", table_name="study_session")
    op.drop_index("ix_word_topic", table_name="word")
    op.drop_index("ix_word_difficulty", table_name="word")
