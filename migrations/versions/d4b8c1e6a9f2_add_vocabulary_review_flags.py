"""add vocabulary review flags

Revision ID: d4b8c1e6a9f2
Revises: c83e51a90d42
Create Date: 2026-05-26 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "d4b8c1e6a9f2"
down_revision = "c83e51a90d42"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "vocabulary_review_flags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("vocabulary_id", sa.Integer(), nullable=True),
        sa.Column("original_word", sa.String(length=180), nullable=False),
        sa.Column("corrected_word", sa.String(length=180), nullable=True),
        sa.Column("flag_type", sa.String(length=60), nullable=False),
        sa.Column("status", sa.String(length=30), server_default="pending", nullable=False),
        sa.Column("level", sa.String(length=40), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["vocabulary_id"], ["vocabulary_master.id"]),
    )
    op.create_index("ix_vocabulary_review_flags_status", "vocabulary_review_flags", ["status"])
    op.create_index("ix_vocabulary_review_flags_flag_type", "vocabulary_review_flags", ["flag_type"])
    op.create_index("ix_vocabulary_review_flags_vocabulary_id", "vocabulary_review_flags", ["vocabulary_id"])


def downgrade():
    op.drop_index("ix_vocabulary_review_flags_vocabulary_id", table_name="vocabulary_review_flags")
    op.drop_index("ix_vocabulary_review_flags_flag_type", table_name="vocabulary_review_flags")
    op.drop_index("ix_vocabulary_review_flags_status", table_name="vocabulary_review_flags")
    op.drop_table("vocabulary_review_flags")
