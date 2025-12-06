"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-12-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables for Mluv.Me."""

    def _ensure_enum_type(name: str, values: list[str]) -> None:
        """Create enum type if missing to handle reruns safely."""
        values_sql = ", ".join(f"'{v}'" for v in values)
        op.execute(
            sa.text(
                f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_type t
                        JOIN pg_namespace n ON n.oid = t.typnamespace
                        WHERE n.nspname = current_schema()
                          AND t.typname = '{name}'
                    ) THEN
                        EXECUTE format(
                            'CREATE TYPE %I AS ENUM ({values_sql})',
                            '{name}'
                        );
                    END IF;
                END $$;
                """
            )
        )

    # Create enums
    ui_language_enum = postgresql.ENUM(
        'ru', 'uk', name='ui_language_enum', create_type=False
    )
    level_enum = postgresql.ENUM(
        'beginner', 'intermediate', 'advanced', 'native',
        name='level_enum',
        create_type=False,
    )
    conversation_style_enum = postgresql.ENUM(
        'friendly', 'tutor', 'casual',
        name='conversation_style_enum',
        create_type=False,
    )
    voice_speed_enum = postgresql.ENUM(
        'very_slow', 'slow', 'normal', 'native',
        name='voice_speed_enum',
        create_type=False,
    )
    corrections_level_enum = postgresql.ENUM(
        'minimal', 'balanced', 'detailed',
        name='corrections_level_enum',
        create_type=False,
    )
    message_role_enum = postgresql.ENUM(
        'user', 'assistant',
        name='message_role_enum',
        create_type=False,
    )

    # Ensure enum types exist (safe for reruns)
    _ensure_enum_type('ui_language_enum', ['ru', 'uk'])
    _ensure_enum_type(
        'level_enum',
        ['beginner', 'intermediate', 'advanced', 'native'],
    )
    _ensure_enum_type('conversation_style_enum', ['friendly', 'tutor', 'casual'])
    _ensure_enum_type('voice_speed_enum', ['very_slow', 'slow', 'normal', 'native'])
    _ensure_enum_type('corrections_level_enum', ['minimal', 'balanced', 'detailed'])
    _ensure_enum_type('message_role_enum', ['user', 'assistant'])

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False, comment='Telegram user ID'),
        sa.Column('username', sa.String(length=255), nullable=True, comment='Telegram username'),
        sa.Column('first_name', sa.String(length=255), nullable=False, comment='Имя пользователя'),
        sa.Column('ui_language', ui_language_enum, nullable=False, server_default='ru',
                  comment='Язык интерфейса (русский или украинский)'),
        sa.Column('level', level_enum, nullable=False, server_default='beginner',
                  comment='Уровень чешского языка'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()'), comment='Дата регистрации'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()'), comment='Дата последнего обновления'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
        sa.UniqueConstraint('telegram_id', name=op.f('uq_users_telegram_id'))
    )
    op.create_index(op.f('ix_telegram_id'), 'users', ['telegram_id'], unique=True)

    # Create user_settings table
    op.create_table(
        'user_settings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='User ID'),
        sa.Column('conversation_style', conversation_style_enum, nullable=False,
                  server_default='friendly', comment='Стиль общения Хонзика'),
        sa.Column('voice_speed', voice_speed_enum, nullable=False,
                  server_default='normal', comment='Скорость голоса Хонзика'),
        sa.Column('corrections_level', corrections_level_enum, nullable=False,
                  server_default='balanced', comment='Уровень исправлений'),
        sa.Column('timezone', sa.String(length=50), nullable=False,
                  server_default='Europe/Prague', comment='Timezone пользователя'),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False,
                  server_default='true', comment='Включены ли уведомления'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'],
                                name=op.f('fk_user_settings_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_user_settings')),
        sa.UniqueConstraint('user_id', name=op.f('uq_user_settings_user_id'))
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='User ID'),
        sa.Column('role', message_role_enum, nullable=False,
                  comment='Роль отправителя (user или assistant/Honzík)'),
        sa.Column('text', sa.Text(), nullable=False, comment='Текст сообщения'),
        sa.Column('transcript_raw', sa.Text(), nullable=True,
                  comment='Оригинальная транскрипция STT'),
        sa.Column('transcript_normalized', sa.Text(), nullable=True,
                  comment='Нормализованный/исправленный текст'),
        sa.Column('audio_file_path', sa.String(length=500), nullable=True,
                  comment='Путь к аудио файлу'),
        sa.Column('correctness_score', sa.Integer(), nullable=True,
                  comment='Оценка правильности (0-100)'),
        sa.Column('words_total', sa.Integer(), nullable=True,
                  server_default='0', comment='Количество слов'),
        sa.Column('words_correct', sa.Integer(), nullable=True,
                  server_default='0', comment='Правильных слов'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()'), comment='Дата создания'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'],
                                name=op.f('fk_messages_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_messages'))
    )
    op.create_index(op.f('ix_messages_user_id'), 'messages', ['user_id'])
    op.create_index(op.f('ix_messages_created_at'), 'messages', ['created_at'])

    # Create saved_words table
    op.create_table(
        'saved_words',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='User ID'),
        sa.Column('word_czech', sa.String(length=255), nullable=False,
                  comment='Чешское слово'),
        sa.Column('translation', sa.String(length=500), nullable=False,
                  comment='Перевод на родной язык'),
        sa.Column('context_sentence', sa.Text(), nullable=True,
                  comment='Предложение-контекст'),
        sa.Column('phonetics', sa.String(length=255), nullable=True,
                  comment='Фонетическая транскрипция'),
        sa.Column('times_reviewed', sa.Integer(), nullable=False,
                  server_default='0', comment='Сколько раз повторялось'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()'), comment='Дата добавления'),
        sa.Column('last_reviewed_at', sa.DateTime(timezone=True), nullable=True,
                  comment='Дата последнего повторения'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'],
                                name=op.f('fk_saved_words_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_saved_words'))
    )
    op.create_index(op.f('ix_saved_words_user_id'), 'saved_words', ['user_id'])

    # Create daily_stats table
    op.create_table(
        'daily_stats',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='User ID'),
        sa.Column('date', sa.Date(), nullable=False, comment='Дата статистики'),
        sa.Column('messages_count', sa.Integer(), nullable=False,
                  server_default='0', comment='Количество сообщений за день'),
        sa.Column('words_said', sa.Integer(), nullable=False,
                  server_default='0', comment='Слов сказано за день'),
        sa.Column('correct_percent', sa.Integer(), nullable=False,
                  server_default='0', comment='Средний процент правильных за день'),
        sa.Column('streak_day', sa.Integer(), nullable=False,
                  server_default='0', comment='День streak подряд'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()'), comment='Дата создания записи'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'],
                                name=op.f('fk_daily_stats_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_daily_stats'))
    )
    op.create_index(op.f('ix_daily_stats_user_id'), 'daily_stats', ['user_id'])
    op.create_index(op.f('ix_daily_stats_date'), 'daily_stats', ['date'])

    # Create stars table
    op.create_table(
        'stars',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='User ID'),
        sa.Column('total', sa.Integer(), nullable=False,
                  server_default='0', comment='Всего заработано звезд (текущий баланс)'),
        sa.Column('available', sa.Integer(), nullable=False,
                  server_default='0', comment='Доступно для обмена'),
        sa.Column('lifetime', sa.Integer(), nullable=False,
                  server_default='0', comment='За все время (не может уменьшаться)'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()'), comment='Дата последнего обновления'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'],
                                name=op.f('fk_stars_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_stars')),
        sa.UniqueConstraint('user_id', name=op.f('uq_stars_user_id'))
    )


def downgrade() -> None:
    """Drop all tables."""

    # Drop tables in reverse order
    op.drop_table('stars')
    op.drop_index(op.f('ix_daily_stats_date'), table_name='daily_stats')
    op.drop_index(op.f('ix_daily_stats_user_id'), table_name='daily_stats')
    op.drop_table('daily_stats')

    op.drop_index(op.f('ix_saved_words_user_id'), table_name='saved_words')
    op.drop_table('saved_words')

    op.drop_index(op.f('ix_messages_created_at'), table_name='messages')
    op.drop_index(op.f('ix_messages_user_id'), table_name='messages')
    op.drop_table('messages')

    op.drop_table('user_settings')

    op.drop_index(op.f('ix_telegram_id'), table_name='users')
    op.drop_table('users')

    # Drop enums
    postgresql.ENUM(name='message_role_enum', create_type=False).drop(
        op.get_bind(), checkfirst=True
    )
    postgresql.ENUM(name='corrections_level_enum', create_type=False).drop(
        op.get_bind(), checkfirst=True
    )
    postgresql.ENUM(name='voice_speed_enum', create_type=False).drop(
        op.get_bind(), checkfirst=True
    )
    postgresql.ENUM(name='conversation_style_enum', create_type=False).drop(
        op.get_bind(), checkfirst=True
    )
    postgresql.ENUM(name='level_enum', create_type=False).drop(
        op.get_bind(), checkfirst=True
    )
    postgresql.ENUM(name='ui_language_enum', create_type=False).drop(
        op.get_bind(), checkfirst=True
    )

