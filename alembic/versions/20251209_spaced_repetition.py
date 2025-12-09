"""
Add spaced repetition fields to saved_words.

Revision ID: 20251209_spaced_repetition
Revises: 003
Create Date: 2025-12-09
"""

from alembic import op
import sqlalchemy as sa
from datetime import date


# revision identifiers, used by Alembic.
revision = '20251209_spaced_repetition'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add spaced repetition columns to saved_words table."""
    # Add ease_factor - SM-2 algorithm factor (starts at 2.5)
    op.add_column(
        'saved_words',
        sa.Column('ease_factor', sa.Float, nullable=False, server_default='2.5')
    )

    # Add interval_days - days until next review
    op.add_column(
        'saved_words',
        sa.Column('interval_days', sa.Integer, nullable=False, server_default='1')
    )

    # Add next_review_date - when the word should be reviewed
    op.add_column(
        'saved_words',
        sa.Column('next_review_date', sa.Date, nullable=True)
    )

    # Add review_count - total number of reviews
    op.add_column(
        'saved_words',
        sa.Column('sr_review_count', sa.Integer, nullable=False, server_default='0')
    )

    # Add quality_history - track last 5 quality ratings as JSON
    op.add_column(
        'saved_words',
        sa.Column('quality_history', sa.Text, nullable=True)
    )

    # Set initial next_review_date to today for existing words
    op.execute(
        f"UPDATE saved_words SET next_review_date = '{date.today().isoformat()}' WHERE next_review_date IS NULL"
    )

    # Create index for efficient querying of words due for review
    op.create_index(
        'ix_saved_words_next_review',
        'saved_words',
        ['user_id', 'next_review_date'],
        unique=False
    )


def downgrade() -> None:
    """Remove spaced repetition columns."""
    op.drop_index('ix_saved_words_next_review', table_name='saved_words')
    op.drop_column('saved_words', 'quality_history')
    op.drop_column('saved_words', 'sr_review_count')
    op.drop_column('saved_words', 'next_review_date')
    op.drop_column('saved_words', 'interval_days')
    op.drop_column('saved_words', 'ease_factor')
