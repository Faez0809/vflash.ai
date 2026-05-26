"""add user level progress

Revision ID: ab42f1d7c903
Revises: f7d2c9a4b601
Create Date: 2026-05-25 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "ab42f1d7c903"
down_revision = "f7d2c9a4b601"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_level_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("level", sa.String(length=40), nullable=False),
        sa.Column("last_alphabetical_word_id", sa.Integer(), nullable=True),
        sa.Column("completed_percentage", sa.Float(), server_default="0", nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["last_alphabetical_word_id"], ["vocabulary_master.id"]),
        sa.UniqueConstraint("user_id", "level", name="uq_user_level_progress_user_level"),
    )
    op.create_index("ix_user_level_progress_user_id", "user_level_progress", ["user_id"])
    op.create_index("ix_user_level_progress_level", "user_level_progress", ["level"])


def downgrade():
    op.drop_index("ix_user_level_progress_level", table_name="user_level_progress")
    op.drop_index("ix_user_level_progress_user_id", table_name="user_level_progress")
    op.drop_table("user_level_progress")
