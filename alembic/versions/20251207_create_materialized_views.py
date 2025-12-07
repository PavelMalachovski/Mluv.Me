"""Create materialized views for analytics

Revision ID: 003
Revises: 002
Create Date: 2025-12-07 14:00:00.000000

This migration creates materialized views for fast analytics queries:
- user_stats_summary: Aggregated user statistics (messages, correctness, streaks, stars)
This view speeds up dashboard and leaderboard queries by 10x+
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create materialized views for analytics.

    Materialized views precompute and store results of complex queries,
    making dashboard and analytics queries much faster.

    Note: Initial indexes are created without CONCURRENTLY.
    In production, use CONCURRENTLY for manual index creation.
    """

    # Create user_stats_summary materialized view
    op.execute(
        sa.text("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS user_stats_summary AS
            SELECT
                u.id,
                u.telegram_id,
                u.first_name,
                u.username,
                u.level,
                u.created_at,

                -- Message statistics
                COUNT(DISTINCT m.id) FILTER (WHERE m.role = 'user') as total_messages,
                COUNT(DISTINCT m.id) FILTER (
                    WHERE m.role = 'user'
                    AND m.created_at >= CURRENT_DATE - INTERVAL '7 days'
                ) as messages_last_7_days,
                COUNT(DISTINCT m.id) FILTER (
                    WHERE m.role = 'user'
                    AND m.created_at >= CURRENT_DATE - INTERVAL '30 days'
                ) as messages_last_30_days,

                -- Correctness statistics
                COALESCE(AVG(m.correctness_score) FILTER (WHERE m.correctness_score IS NOT NULL), 0)::INTEGER as avg_correctness,
                COALESCE(
                    AVG(m.correctness_score) FILTER (
                        WHERE m.correctness_score IS NOT NULL
                        AND m.created_at >= CURRENT_DATE - INTERVAL '7 days'
                    ),
                    0
                )::INTEGER as avg_correctness_7_days,

                -- Streak statistics
                COALESCE(MAX(ds.streak_day), 0) as max_streak,
                COALESCE(
                    (SELECT ds2.streak_day
                     FROM daily_stats ds2
                     WHERE ds2.user_id = u.id
                     ORDER BY ds2.date DESC
                     LIMIT 1),
                    0
                ) as current_streak,

                -- Stars
                COALESCE(s.total, 0) as total_stars,
                COALESCE(s.lifetime, 0) as lifetime_stars,

                -- Activity
                MAX(m.created_at) as last_activity,

                -- Words statistics
                COALESCE(SUM(ds.words_said), 0) as total_words_said,
                COUNT(DISTINCT sw.id) as saved_words_count

            FROM users u
            LEFT JOIN messages m ON m.user_id = u.id
            LEFT JOIN daily_stats ds ON ds.user_id = u.id
            LEFT JOIN stars s ON s.user_id = u.id
            LEFT JOIN saved_words sw ON sw.user_id = u.id
            GROUP BY u.id, u.telegram_id, u.first_name, u.username, u.level, u.created_at, s.total, s.lifetime
        """)
    )

    # Create indexes on materialized view for fast queries
    op.create_index(
        'idx_user_stats_summary_telegram_id',
        'user_stats_summary',
        ['telegram_id'],
        unique=False
    )

    op.execute(
        sa.text("""
            CREATE INDEX idx_user_stats_summary_total_stars
            ON user_stats_summary(total_stars DESC)
        """)
    )

    op.execute(
        sa.text("""
            CREATE INDEX idx_user_stats_summary_max_streak
            ON user_stats_summary(max_streak DESC)
        """)
    )

    op.execute(
        sa.text("""
            CREATE INDEX idx_user_stats_summary_total_messages
            ON user_stats_summary(total_messages DESC)
        """)
    )

    op.execute(
        sa.text("""
            CREATE INDEX idx_user_stats_summary_last_activity
            ON user_stats_summary(last_activity DESC NULLS LAST)
        """)
    )


def downgrade() -> None:
    """
    Drop materialized views and indexes.
    """

    # Drop materialized view (this will also drop all indexes on it)
    op.execute(sa.text("DROP MATERIALIZED VIEW IF EXISTS user_stats_summary CASCADE"))
