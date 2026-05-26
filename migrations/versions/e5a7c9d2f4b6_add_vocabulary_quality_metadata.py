"""add vocabulary quality metadata

Revision ID: e5a7c9d2f4b6
Revises: d4b8c1e6a9f2
Create Date: 2026-05-26 03:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "e5a7c9d2f4b6"
down_revision = "d4b8c1e6a9f2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("vocabulary_master", sa.Column("needs_admin_review", sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column("vocabulary_master", sa.Column("review_reason", sa.Text(), nullable=True))
    op.add_column("vocabulary_master", sa.Column("original_word", sa.String(length=180), nullable=True))
    op.add_column("vocabulary_master", sa.Column("corrected_at", sa.DateTime(), nullable=True))
    op.add_column("vocabulary_master", sa.Column("corrected_by_admin", sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column("vocabulary_master", sa.Column("last_audited_at", sa.DateTime(), nullable=True))
    op.add_column("vocabulary_enrichment", sa.Column("last_audited_at", sa.DateTime(), nullable=True))
    op.add_column("vocabulary_enrichment", sa.Column("last_regenerated_at", sa.DateTime(), nullable=True))
    op.create_index("ix_vocabulary_master_needs_admin_review", "vocabulary_master", ["needs_admin_review"])
    op.create_index("ix_vocabulary_master_last_audited", "vocabulary_master", ["last_audited_at"])


def downgrade():
    op.drop_index("ix_vocabulary_master_last_audited", table_name="vocabulary_master")
    op.drop_index("ix_vocabulary_master_needs_admin_review", table_name="vocabulary_master")
    op.drop_column("vocabulary_enrichment", "last_regenerated_at")
    op.drop_column("vocabulary_enrichment", "last_audited_at")
    op.drop_column("vocabulary_master", "last_audited_at")
    op.drop_column("vocabulary_master", "corrected_by_admin")
    op.drop_column("vocabulary_master", "corrected_at")
    op.drop_column("vocabulary_master", "original_word")
    op.drop_column("vocabulary_master", "review_reason")
    op.drop_column("vocabulary_master", "needs_admin_review")
