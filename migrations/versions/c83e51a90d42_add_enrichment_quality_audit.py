"""add enrichment quality audit fields

Revision ID: c83e51a90d42
Revises: ab42f1d7c903
Create Date: 2026-05-25 23:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "c83e51a90d42"
down_revision = "ab42f1d7c903"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("vocabulary_enrichment", sa.Column("enrichment_quality_score", sa.Integer(), server_default="0", nullable=False))
    op.add_column("vocabulary_enrichment", sa.Column("audit_flags", sa.Text(), nullable=True))
    op.add_column("vocabulary_enrichment", sa.Column("generated_by_model", sa.String(length=120), nullable=True))
    op.add_column("vocabulary_enrichment", sa.Column("corrected_manually", sa.Boolean(), server_default=sa.false(), nullable=False))


def downgrade():
    op.drop_column("vocabulary_enrichment", "corrected_manually")
    op.drop_column("vocabulary_enrichment", "generated_by_model")
    op.drop_column("vocabulary_enrichment", "audit_flags")
    op.drop_column("vocabulary_enrichment", "enrichment_quality_score")
