"""fix boolean server defaults

Revision ID: e6f9b7d4c2a1
Revises: c1a2f0e4b8d3
Create Date: 2026-04-13 22:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e6f9b7d4c2a1"
down_revision = "c1a2f0e4b8d3"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("word", "is_valid", server_default=sa.true(), existing_type=sa.Boolean(), existing_nullable=False)
    op.alter_column("user", "is_restricted", server_default=sa.false(), existing_type=sa.Boolean(), existing_nullable=False)
    op.alter_column("user_word", "already_known", server_default=sa.false(), existing_type=sa.Boolean(), existing_nullable=False)
    op.alter_column("user_word", "is_difficult", server_default=sa.false(), existing_type=sa.Boolean(), existing_nullable=False)
    op.alter_column("user_word", "is_favorite", server_default=sa.false(), existing_type=sa.Boolean(), existing_nullable=False)
    op.alter_column("quiz_history", "was_quit", server_default=sa.false(), existing_type=sa.Boolean(), existing_nullable=False)


def downgrade():
    op.alter_column("quiz_history", "was_quit", server_default=None, existing_type=sa.Boolean(), existing_nullable=False)
    op.alter_column("user_word", "is_favorite", server_default=None, existing_type=sa.Boolean(), existing_nullable=False)
    op.alter_column("user_word", "is_difficult", server_default=None, existing_type=sa.Boolean(), existing_nullable=False)
    op.alter_column("user_word", "already_known", server_default=None, existing_type=sa.Boolean(), existing_nullable=False)
    op.alter_column("user", "is_restricted", server_default=None, existing_type=sa.Boolean(), existing_nullable=False)
    op.alter_column("word", "is_valid", server_default=None, existing_type=sa.Boolean(), existing_nullable=False)
