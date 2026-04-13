"""add word validity flag

Revision ID: c1a2f0e4b8d3
Revises: 9f4b7c2a1d10
Create Date: 2026-04-13 22:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c1a2f0e4b8d3"
down_revision = "9f4b7c2a1d10"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "word",
        sa.Column("is_valid", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_word_is_valid", "word", ["is_valid"], unique=False)
    op.alter_column("word", "is_valid", server_default=None)


def downgrade():
    op.drop_index("ix_word_is_valid", table_name="word")
    op.drop_column("word", "is_valid")
