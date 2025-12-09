"""
Add achievements table for gamification.

Revision ID: 20251209_gamification
Revises: 20251209_spaced_repetition
Create Date: 2025-12-09
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '20251209_gamification'
down_revision = '20251209_spaced_repetition'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create achievements and user_achievements tables."""

    # Create achievements table (achievement definitions)
    op.create_table(
        'achievements',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('code', sa.String(50), unique=True, nullable=False, comment='Unique achievement code'),
        sa.Column('name', sa.String(100), nullable=False, comment='Display name'),
        sa.Column('description', sa.String(500), nullable=False, comment='Achievement description'),
        sa.Column('icon', sa.String(10), nullable=False, comment='Emoji icon'),
        sa.Column('category', sa.String(50), nullable=False, comment='Category: streak, messages, vocabulary, accuracy'),
        sa.Column('threshold', sa.Integer, nullable=False, comment='Value needed to unlock'),
        sa.Column('stars_reward', sa.Integer, nullable=False, default=0, comment='Stars awarded'),
        sa.Column('is_hidden', sa.Boolean, nullable=False, default=False, comment='Hidden until unlocked'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create user_achievements table (tracking unlocked achievements)
    op.create_table(
        'user_achievements',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('achievement_id', sa.Integer, sa.ForeignKey('achievements.id', ondelete='CASCADE'), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('progress', sa.Integer, nullable=False, default=0, comment='Current progress towards achievement'),
    )

    # Create unique constraint for user + achievement
    op.create_unique_constraint(
        'uq_user_achievement',
        'user_achievements',
        ['user_id', 'achievement_id']
    )

    # Create index for faster lookups
    op.create_index('ix_user_achievements_user_id', 'user_achievements', ['user_id'])

    # Insert default achievements
    achievements_table = sa.table(
        'achievements',
        sa.column('code', sa.String),
        sa.column('name', sa.String),
        sa.column('description', sa.String),
        sa.column('icon', sa.String),
        sa.column('category', sa.String),
        sa.column('threshold', sa.Integer),
        sa.column('stars_reward', sa.Integer),
        sa.column('is_hidden', sa.Boolean),
    )

    op.bulk_insert(achievements_table, [
        # Streak achievements
        {'code': 'streak_3', 'name': 'Getting Started', 'description': '3 day streak', 'icon': '🔥', 'category': 'streak', 'threshold': 3, 'stars_reward': 5, 'is_hidden': False},
        {'code': 'streak_7', 'name': 'Week Warrior', 'description': '7 day streak', 'icon': '🔥', 'category': 'streak', 'threshold': 7, 'stars_reward': 15, 'is_hidden': False},
        {'code': 'streak_30', 'name': 'Monthly Master', 'description': '30 day streak', 'icon': '🔥', 'category': 'streak', 'threshold': 30, 'stars_reward': 50, 'is_hidden': False},
        {'code': 'streak_100', 'name': 'Centurion', 'description': '100 day streak', 'icon': '💯', 'category': 'streak', 'threshold': 100, 'stars_reward': 200, 'is_hidden': True},

        # Message achievements
        {'code': 'messages_10', 'name': 'First Steps', 'description': 'Send 10 messages', 'icon': '💬', 'category': 'messages', 'threshold': 10, 'stars_reward': 5, 'is_hidden': False},
        {'code': 'messages_50', 'name': 'Chatty', 'description': 'Send 50 messages', 'icon': '💬', 'category': 'messages', 'threshold': 50, 'stars_reward': 15, 'is_hidden': False},
        {'code': 'messages_200', 'name': 'Conversationalist', 'description': 'Send 200 messages', 'icon': '🗣️', 'category': 'messages', 'threshold': 200, 'stars_reward': 50, 'is_hidden': False},
        {'code': 'messages_1000', 'name': 'Czech Master', 'description': 'Send 1000 messages', 'icon': '👑', 'category': 'messages', 'threshold': 1000, 'stars_reward': 200, 'is_hidden': True},

        # Vocabulary achievements
        {'code': 'vocab_10', 'name': 'Word Collector', 'description': 'Save 10 words', 'icon': '📚', 'category': 'vocabulary', 'threshold': 10, 'stars_reward': 5, 'is_hidden': False},
        {'code': 'vocab_50', 'name': 'Vocabulary Builder', 'description': 'Save 50 words', 'icon': '📚', 'category': 'vocabulary', 'threshold': 50, 'stars_reward': 15, 'is_hidden': False},
        {'code': 'vocab_200', 'name': 'Walking Dictionary', 'description': 'Save 200 words', 'icon': '📖', 'category': 'vocabulary', 'threshold': 200, 'stars_reward': 50, 'is_hidden': False},

        # Accuracy achievements
        {'code': 'accuracy_90', 'name': 'Sharp Mind', 'description': '90% accuracy in a session', 'icon': '🎯', 'category': 'accuracy', 'threshold': 90, 'stars_reward': 10, 'is_hidden': False},
        {'code': 'perfect_session', 'name': 'Perfectionist', 'description': 'Perfect review session (10+ words)', 'icon': '⭐', 'category': 'accuracy', 'threshold': 100, 'stars_reward': 25, 'is_hidden': False},

        # Stars achievements
        {'code': 'stars_100', 'name': 'Star Collector', 'description': 'Collect 100 stars', 'icon': '⭐', 'category': 'stars', 'threshold': 100, 'stars_reward': 20, 'is_hidden': False},
        {'code': 'stars_500', 'name': 'Star Hunter', 'description': 'Collect 500 stars', 'icon': '🌟', 'category': 'stars', 'threshold': 500, 'stars_reward': 50, 'is_hidden': False},
        {'code': 'stars_1000', 'name': 'Superstar', 'description': 'Collect 1000 stars', 'icon': '✨', 'category': 'stars', 'threshold': 1000, 'stars_reward': 100, 'is_hidden': True},

        # Review achievements
        {'code': 'review_mastered_10', 'name': 'Memory Pro', 'description': 'Master 10 words', 'icon': '🧠', 'category': 'review', 'threshold': 10, 'stars_reward': 15, 'is_hidden': False},
        {'code': 'review_mastered_50', 'name': 'Memory Champion', 'description': 'Master 50 words', 'icon': '🏆', 'category': 'review', 'threshold': 50, 'stars_reward': 50, 'is_hidden': False},
    ])


def downgrade() -> None:
    """Remove achievements tables."""
    op.drop_table('user_achievements')
    op.drop_table('achievements')
