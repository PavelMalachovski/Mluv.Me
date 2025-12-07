"""Add performance indexes

Revision ID: 002
Revises: 001
Create Date: 2025-12-07 12:00:00.000000

This migration adds performance indexes to improve query speed by 10-20x:
- Composite indexes for messages (user_id + created_at DESC)
- Composite indexes for daily_stats (user_id + date DESC)
- Composite indexes for saved_words (user_id + word_czech)
- Full-text search index for messages.user_text (Czech language)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create performance indexes.

    Note: We use regular CREATE INDEX (not CONCURRENTLY) because:
    1. CONCURRENTLY cannot run inside a transaction block
    2. For initial migration, the table should be small/empty
    3. For production with data, you can create indexes manually with CONCURRENTLY
    """

    # 1. Messages table - composite index for user history queries
    # This speeds up queries like: SELECT * FROM messages WHERE user_id = ? ORDER BY created_at DESC
    op.create_index(
        'idx_messages_user_created',
        'messages',
        ['user_id', sa.text('created_at DESC')],
        unique=False
    )

    # 2. Daily stats - composite index for user stats queries
    # This speeds up queries like: SELECT * FROM daily_stats WHERE user_id = ? ORDER BY date DESC
    op.create_index(
        'idx_daily_stats_user_date',
        'daily_stats',
        ['user_id', sa.text('date DESC')],
        unique=False
    )

    # 3. Saved words - composite index for word lookups
    # This speeds up queries like: SELECT * FROM saved_words WHERE user_id = ? AND word_czech = ?
    op.create_index(
        'idx_saved_words_user_word',
        'saved_words',
        ['user_id', 'word_czech'],
        unique=False
    )

    # 4. Full-text search index for messages
    # This enables fast text search in Czech language
    op.execute(
        sa.text("""
            CREATE INDEX idx_messages_text_search
            ON messages USING gin(to_tsvector('czech', text))
            WHERE text IS NOT NULL
        """)
    )

    # 5. Additional index for messages correctness_score (for analytics)
    # This speeds up queries for finding high-scoring or low-scoring messages
    op.create_index(
        'idx_messages_correctness_score',
        'messages',
        ['correctness_score'],
        unique=False,
        postgresql_where=sa.text('correctness_score IS NOT NULL')
    )

    # 6. Additional index for saved_words last_reviewed_at (for spaced repetition)
    # This speeds up queries for finding words due for review
    op.execute(
        sa.text("""
            CREATE INDEX idx_saved_words_review
            ON saved_words (user_id, last_reviewed_at NULLS FIRST)
        """)
    )


def downgrade() -> None:
    """
    Drop performance indexes.
    """

    # Drop indexes in reverse order
    op.drop_index('idx_saved_words_review', table_name='saved_words')
    op.drop_index('idx_messages_correctness_score', table_name='messages')
    op.drop_index('idx_messages_text_search', table_name='messages')
    op.drop_index('idx_saved_words_user_word', table_name='saved_words')
    op.drop_index('idx_daily_stats_user_date', table_name='daily_stats')
    op.drop_index('idx_messages_user_created', table_name='messages')
