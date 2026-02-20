"""add character column to user_settings

Revision ID: 20260220_add_character
Revises: 20260210_grammar_rules
Create Date: 2026-02-20

Adds `character` column to `user_settings` table.
Default value is 'honzik'. New option: 'novakova'.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260220_add_character"
down_revision = "20260210_grammar_rules"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_settings",
        sa.Column(
            "character",
            sa.String(20),
            nullable=False,
            server_default="honzik",
            comment="Vybraná postava pro konverzaci (honzik, novakova)",
        ),
    )


def downgrade() -> None:
    op.drop_column("user_settings", "character")
