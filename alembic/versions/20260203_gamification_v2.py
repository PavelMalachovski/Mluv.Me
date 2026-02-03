"""
Gamification V2: Extended achievements, challenges, and leaderboard.

Revision ID: 20260203_gamification_v2
Revises: 20260203_czech_only_ui
Create Date: 2026-02-03
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '20260203_gamification_v2'
down_revision = '20260203_czech_only_ui'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add extended gamification features:
    1. New achievement categories (thematic, time, quality)
    2. Challenges system (daily/weekly)
    3. User privacy settings for leaderboard
    4. Topic message counters
    """

    # Add privacy setting for leaderboard visibility
    op.add_column(
        'user_settings',
        sa.Column(
            'leaderboard_visible',
            sa.Boolean,
            nullable=False,
            server_default=sa.text('true'),
            comment='Show user in public leaderboard'
        )
    )

    # Create challenges table
    op.create_table(
        'challenges',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('code', sa.String(50), unique=True, nullable=False, comment='Unique challenge code'),
        sa.Column('type', sa.String(20), nullable=False, comment='daily/weekly/special'),
        sa.Column('title_cs', sa.String(100), nullable=False, comment='Czech title'),
        sa.Column('description_cs', sa.String(500), nullable=False, comment='Czech description'),
        sa.Column('goal_type', sa.String(50), nullable=False, comment='messages/high_accuracy_messages/saved_words/topic_message/streak_days'),
        sa.Column('goal_topic', sa.String(50), nullable=True, comment='Topic for topic_message goal type'),
        sa.Column('goal_value', sa.Integer, nullable=False, comment='Target value'),
        sa.Column('reward_stars', sa.Integer, nullable=False, default=5, comment='Stars reward'),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.text('true'), comment='Is challenge active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create user_challenges table (tracking user challenge progress)
    op.create_table(
        'user_challenges',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('challenge_id', sa.Integer, sa.ForeignKey('challenges.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.Date, nullable=False, comment='Challenge date (for daily/weekly)'),
        sa.Column('progress', sa.Integer, nullable=False, default=0, comment='Current progress'),
        sa.Column('completed', sa.Boolean, nullable=False, server_default=sa.text('false'), comment='Challenge completed'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='Completion timestamp'),
        sa.Column('reward_claimed', sa.Boolean, nullable=False, server_default=sa.text('false'), comment='Reward claimed'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create unique constraint for user + challenge + date
    op.create_unique_constraint(
        'uq_user_challenge_date',
        'user_challenges',
        ['user_id', 'challenge_id', 'date']
    )

    # Create indexes for challenges
    op.create_index('ix_user_challenges_user_id', 'user_challenges', ['user_id'])
    op.create_index('ix_user_challenges_date', 'user_challenges', ['date'])

    # Create topic_message_counts table (for thematic achievements)
    op.create_table(
        'topic_message_counts',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('topic', sa.String(50), nullable=False, comment='Topic: beer, food, history, travel, etc.'),
        sa.Column('count', sa.Integer, nullable=False, default=0, comment='Number of messages on this topic'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create unique constraint for user + topic
    op.create_unique_constraint(
        'uq_user_topic',
        'topic_message_counts',
        ['user_id', 'topic']
    )
    op.create_index('ix_topic_message_counts_user_id', 'topic_message_counts', ['user_id'])

    # Insert new achievements (thematic, time-based, quality)
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
        # === Thematic achievements ===
        {
            'code': 'beer_master',
            'name': '🍺 Pivař',
            'description': '10 konverzací o pivu',
            'icon': '🍺',
            'category': 'thematic',
            'threshold': 10,
            'stars_reward': 25,
            'is_hidden': False,
        },
        {
            'code': 'foodie',
            'name': '🥟 Gurmán',
            'description': '10 konverzací o jídle',
            'icon': '🥟',
            'category': 'thematic',
            'threshold': 10,
            'stars_reward': 25,
            'is_hidden': False,
        },
        {
            'code': 'history_buff',
            'name': '🏰 Historik',
            'description': '5 konverzací o historii',
            'icon': '🏰',
            'category': 'thematic',
            'threshold': 5,
            'stars_reward': 20,
            'is_hidden': False,
        },
        {
            'code': 'traveler',
            'name': '✈️ Cestovatel',
            'description': '5 konverzací o cestování',
            'icon': '✈️',
            'category': 'thematic',
            'threshold': 5,
            'stars_reward': 20,
            'is_hidden': False,
        },
        {
            'code': 'culture_lover',
            'name': '🎭 Kulturní znalec',
            'description': '5 konverzací o kultuře',
            'icon': '🎭',
            'category': 'thematic',
            'threshold': 5,
            'stars_reward': 20,
            'is_hidden': False,
        },

        # === Time-based achievements ===
        {
            'code': 'early_bird',
            'name': '🌅 Ranní ptáče',
            'description': 'Procvičování před 7:00',
            'icon': '🌅',
            'category': 'time',
            'threshold': 1,
            'stars_reward': 10,
            'is_hidden': True,
        },
        {
            'code': 'night_owl',
            'name': '🦉 Noční sova',
            'description': 'Procvičování po 23:00',
            'icon': '🦉',
            'category': 'time',
            'threshold': 1,
            'stars_reward': 10,
            'is_hidden': True,
        },
        {
            'code': 'weekend_warrior',
            'name': '🎉 Víkendový bojovník',
            'description': 'Procvičování oba víkendové dny',
            'icon': '🎉',
            'category': 'time',
            'threshold': 1,
            'stars_reward': 15,
            'is_hidden': True,
        },
        {
            'code': 'early_bird_10',
            'name': '🌄 Ranní mistr',
            'description': '10x procvičování před 7:00',
            'icon': '🌄',
            'category': 'time',
            'threshold': 10,
            'stars_reward': 30,
            'is_hidden': True,
        },
        {
            'code': 'night_owl_10',
            'name': '🌙 Noční mistr',
            'description': '10x procvičování po 23:00',
            'icon': '🌙',
            'category': 'time',
            'threshold': 10,
            'stars_reward': 30,
            'is_hidden': True,
        },

        # === Quality achievements ===
        {
            'code': 'perfectionist_3',
            'name': '✨ Perfekcionista',
            'description': '3 zprávy po sobě s >90%',
            'icon': '✨',
            'category': 'quality',
            'threshold': 3,
            'stars_reward': 20,
            'is_hidden': False,
        },
        {
            'code': 'perfectionist_5',
            'name': '💎 Diamantová přesnost',
            'description': '5 zpráv po sobě s >90%',
            'icon': '💎',
            'category': 'quality',
            'threshold': 5,
            'stars_reward': 50,
            'is_hidden': True,
        },
        {
            'code': 'improver_20',
            'name': '📈 Rychlý pokrok',
            'description': 'Zlepšení přesnosti o 20% za týden',
            'icon': '📈',
            'category': 'quality',
            'threshold': 20,
            'stars_reward': 30,
            'is_hidden': False,
        },
        {
            'code': 'no_mistakes_10',
            'name': '🎯 Bezchybný',
            'description': '10 zpráv bez chyb',
            'icon': '🎯',
            'category': 'quality',
            'threshold': 10,
            'stars_reward': 40,
            'is_hidden': True,
        },

        # === Challenge achievements ===
        {
            'code': 'challenge_5',
            'name': '🏅 Vyzyvatel',
            'description': 'Dokončení 5 výzev',
            'icon': '🏅',
            'category': 'challenge',
            'threshold': 5,
            'stars_reward': 20,
            'is_hidden': False,
        },
        {
            'code': 'challenge_20',
            'name': '🏆 Mistr výzev',
            'description': 'Dokončení 20 výzev',
            'icon': '🏆',
            'category': 'challenge',
            'threshold': 20,
            'stars_reward': 50,
            'is_hidden': False,
        },
        {
            'code': 'weekly_champion',
            'name': '👑 Týdenní šampion',
            'description': 'Dokončení všech výzev za týden',
            'icon': '👑',
            'category': 'challenge',
            'threshold': 7,
            'stars_reward': 75,
            'is_hidden': True,
        },
    ])

    # Insert default challenges
    challenges_table = sa.table(
        'challenges',
        sa.column('code', sa.String),
        sa.column('type', sa.String),
        sa.column('title_cs', sa.String),
        sa.column('description_cs', sa.String),
        sa.column('goal_type', sa.String),
        sa.column('goal_topic', sa.String),
        sa.column('goal_value', sa.Integer),
        sa.column('reward_stars', sa.Integer),
        sa.column('is_active', sa.Boolean),
    )

    op.bulk_insert(challenges_table, [
        # Daily challenges
        {
            'code': 'daily_messages_5',
            'type': 'daily',
            'title_cs': '💬 Pohovoř s Honzíkem',
            'description_cs': 'Pošli 5 zpráv',
            'goal_type': 'messages',
            'goal_topic': None,
            'goal_value': 5,
            'reward_stars': 5,
            'is_active': True,
        },
        {
            'code': 'daily_accuracy_80',
            'type': 'daily',
            'title_cs': '🎯 Mluv správně',
            'description_cs': 'Získej >80% ve 3 zprávách',
            'goal_type': 'high_accuracy_messages',
            'goal_topic': None,
            'goal_value': 3,
            'reward_stars': 10,
            'is_active': True,
        },
        {
            'code': 'daily_words_3',
            'type': 'daily',
            'title_cs': '📚 Rozšiř slovník',
            'description_cs': 'Ulož 3 nová slova',
            'goal_type': 'saved_words',
            'goal_topic': None,
            'goal_value': 3,
            'reward_stars': 8,
            'is_active': True,
        },
        {
            'code': 'daily_topic_beer',
            'type': 'daily',
            'title_cs': '🍺 Pohovoř o pivu',
            'description_cs': 'Povídej si o pivu nebo hospodách',
            'goal_type': 'topic_message',
            'goal_topic': 'beer',
            'goal_value': 1,
            'reward_stars': 5,
            'is_active': True,
        },
        {
            'code': 'daily_topic_food',
            'type': 'daily',
            'title_cs': '🥟 Pohovoř o jídle',
            'description_cs': 'Povídej si o českém jídle',
            'goal_type': 'topic_message',
            'goal_topic': 'food',
            'goal_value': 1,
            'reward_stars': 5,
            'is_active': True,
        },
        {
            'code': 'daily_messages_10',
            'type': 'daily',
            'title_cs': '🔥 Aktivní student',
            'description_cs': 'Pošli 10 zpráv',
            'goal_type': 'messages',
            'goal_topic': None,
            'goal_value': 10,
            'reward_stars': 15,
            'is_active': True,
        },

        # Weekly challenges
        {
            'code': 'weekly_streak_7',
            'type': 'weekly',
            'title_cs': '🔥 Týden bez přestávky',
            'description_cs': 'Procvičuj 7 dní v kuse',
            'goal_type': 'streak_days',
            'goal_topic': None,
            'goal_value': 7,
            'reward_stars': 25,
            'is_active': True,
        },
        {
            'code': 'weekly_messages_30',
            'type': 'weekly',
            'title_cs': '💬 Aktivní týden',
            'description_cs': 'Pošli 30 zpráv za týden',
            'goal_type': 'weekly_messages',
            'goal_topic': None,
            'goal_value': 30,
            'reward_stars': 30,
            'is_active': True,
        },
        {
            'code': 'weekly_accuracy_avg_80',
            'type': 'weekly',
            'title_cs': '🎯 Přesný týden',
            'description_cs': 'Průměrná přesnost >80% za týden',
            'goal_type': 'weekly_accuracy',
            'goal_topic': None,
            'goal_value': 80,
            'reward_stars': 35,
            'is_active': True,
        },
        {
            'code': 'weekly_words_15',
            'type': 'weekly',
            'title_cs': '📖 Slovníkový týden',
            'description_cs': 'Ulož 15 nových slov za týden',
            'goal_type': 'weekly_saved_words',
            'goal_topic': None,
            'goal_value': 15,
            'reward_stars': 25,
            'is_active': True,
        },
    ])


def downgrade() -> None:
    """Remove gamification V2 features."""
    # Drop tables
    op.drop_table('topic_message_counts')
    op.drop_table('user_challenges')
    op.drop_table('challenges')

    # Remove leaderboard_visible column
    op.drop_column('user_settings', 'leaderboard_visible')

    # Remove new achievements (by category)
    op.execute("""
        DELETE FROM achievements
        WHERE category IN ('thematic', 'time', 'quality', 'challenge')
    """)
