"""Remove ui_language, add native_language for explanations.

Переход на полностью чешский интерфейс.
UI на чешском, объяснения ошибок - на родном языке пользователя.

Revision ID: 20260203_czech_only_ui
Revises: 20251209_gamification
Create Date: 2026-02-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260203_czech_only_ui'
down_revision: Union[str, None] = '20251209_gamification'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Миграция на чешский интерфейс.

    1. Добавляем новое поле native_language
    2. Копируем данные из ui_language в native_language
    3. Удаляем старое поле ui_language
    """
    # Создаём новый enum для родного языка (добавляем pl, sk для будущего)
    native_language_enum = sa.Enum('ru', 'uk', 'pl', 'sk', name='native_language_enum')
    native_language_enum.create(op.get_bind(), checkfirst=True)

    # Добавляем новое поле native_language
    op.add_column(
        'users',
        sa.Column(
            'native_language',
            sa.Enum('ru', 'uk', 'pl', 'sk', name='native_language_enum'),
            nullable=True,
            comment='Родной язык пользователя (для объяснения ошибок)'
        )
    )

    # Копируем данные из ui_language в native_language (через text для конвертации enum)
    op.execute("""
        UPDATE users
        SET native_language = ui_language::text::native_language_enum
        WHERE ui_language IS NOT NULL
    """)

    # Устанавливаем значение по умолчанию для NULL
    op.execute("""
        UPDATE users
        SET native_language = 'ru'
        WHERE native_language IS NULL
    """)

    # Делаем поле обязательным
    op.alter_column(
        'users',
        'native_language',
        nullable=False,
        server_default='ru'
    )

    # Удаляем старое поле ui_language
    op.drop_column('users', 'ui_language')

    # Удаляем старый enum
    op.execute("DROP TYPE IF EXISTS ui_language_enum")


def downgrade() -> None:
    """
    Откат миграции - возвращаем ui_language.
    """
    # Создаём старый enum
    ui_language_enum = sa.Enum('ru', 'uk', name='ui_language_enum')
    ui_language_enum.create(op.get_bind(), checkfirst=True)

    # Добавляем старое поле ui_language
    op.add_column(
        'users',
        sa.Column(
            'ui_language',
            sa.Enum('ru', 'uk', name='ui_language_enum'),
            nullable=True,
            comment='Язык интерфейса (русский или украинский)'
        )
    )

    # Копируем данные обратно (только ru и uk)
    op.execute("""
        UPDATE users
        SET ui_language = CASE
            WHEN native_language IN ('ru', 'uk') THEN native_language::text::ui_language_enum
            ELSE 'ru'::ui_language_enum
        END
    """)

    # Делаем поле обязательным
    op.alter_column(
        'users',
        'ui_language',
        nullable=False,
        server_default='ru'
    )

    # Удаляем новое поле native_language
    op.drop_column('users', 'native_language')

    # Удаляем новый enum
    op.execute("DROP TYPE IF EXISTS native_language_enum")
