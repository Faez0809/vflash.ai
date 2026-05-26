"""add quiz tracking fields

Revision ID: b1f4d8a6c902
Revises: e5a7c9d2f4b6
Create Date: 2026-05-26 04:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b1f4d8a6c902"
down_revision = "e5a7c9d2f4b6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("quiz_history", sa.Column("mistakes_json", sa.Text(), nullable=True))
    op.add_column("quiz_history", sa.Column("weak_vocabulary_ids", sa.Text(), nullable=True))
    op.add_column("quiz_history", sa.Column("completion_seconds", sa.Integer(), server_default="0", nullable=False))
    op.add_column("quiz_history", sa.Column("retry_of_quiz_id", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("quiz_history", "retry_of_quiz_id")
    op.drop_column("quiz_history", "completion_seconds")
    op.drop_column("quiz_history", "weak_vocabulary_ids")
    op.drop_column("quiz_history", "mistakes_json")
