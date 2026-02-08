"""
Tests for database repositories.
"""

import pytest
from datetime import date

from backend.db.repositories import (
    UserRepository,
    UserSettingsRepository,
    MessageRepository,
    SavedWordRepository,
    StatsRepository,
)


@pytest.mark.asyncio
class TestUserRepository:
    """Tests for UserRepository."""

    async def test_create_user(self, session, user_data):
        """Test creating a user."""
        repo = UserRepository(session)

        user = await repo.create(**user_data)
        await session.commit()

        assert user.id is not None
        assert user.telegram_id == user_data["telegram_id"]
        assert user.username == user_data["username"]
        assert user.first_name == user_data["first_name"]
        assert user.native_language == user_data["native_language"]
        assert user.level == user_data["level"]

        # Check that settings were created
        assert user.settings is not None
        assert user.settings.conversation_style == "friendly"

    async def test_get_by_id(self, session, user_data):
        """Test getting user by ID."""
        repo = UserRepository(session)

        created_user = await repo.create(**user_data)
        await session.commit()

        user = await repo.get_by_id(created_user.id)

        assert user is not None
        assert user.id == created_user.id
        assert user.telegram_id == user_data["telegram_id"]

    async def test_get_by_telegram_id(self, session, user_data):
        """Test getting user by Telegram ID."""
        repo = UserRepository(session)

        await repo.create(**user_data)
        await session.commit()

        user = await repo.get_by_telegram_id(user_data["telegram_id"])

        assert user is not None
        assert user.telegram_id == user_data["telegram_id"]
        assert user.settings is not None

    async def test_get_nonexistent_user(self, session):
        """Test getting nonexistent user."""
        repo = UserRepository(session)

        user = await repo.get_by_id(999999)

        assert user is None

    async def test_update_user(self, session, user_data):
        """Test updating user."""
        repo = UserRepository(session)

        created_user = await repo.create(**user_data)
        await session.commit()

        updated_user = await repo.update(
            created_user.id,
            level="advanced",
            native_language="uk"
        )

        assert updated_user is not None
        assert updated_user.level == "advanced"
        assert updated_user.native_language == "uk"

    async def test_delete_user(self, session, user_data):
        """Test deleting user."""
        repo = UserRepository(session)

        created_user = await repo.create(**user_data)
        await session.commit()

        result = await repo.delete(created_user.id)

        assert result is True

        # Verify user is deleted
        user = await repo.get_by_id(created_user.id)
        assert user is None


@pytest.mark.asyncio
class TestUserSettingsRepository:
    """Tests for UserSettingsRepository."""

    async def test_get_settings(self, session, user_data):
        """Test getting user settings."""
        user_repo = UserRepository(session)
        settings_repo = UserSettingsRepository(session)

        user = await user_repo.create(**user_data)
        await session.commit()

        settings = await settings_repo.get_by_user_id(user.id)

        assert settings is not None
        assert settings.conversation_style == "friendly"
        assert settings.voice_speed == "normal"
        assert settings.corrections_level == "balanced"

    async def test_update_settings(self, session, user_data):
        """Test updating user settings."""
        user_repo = UserRepository(session)
        settings_repo = UserSettingsRepository(session)

        user = await user_repo.create(**user_data)
        await session.commit()

        updated_settings = await settings_repo.update(
            user.id,
            conversation_style="tutor",
            voice_speed="slow",
            corrections_level="detailed"
        )

        assert updated_settings is not None
        assert updated_settings.conversation_style == "tutor"
        assert updated_settings.voice_speed == "slow"
        assert updated_settings.corrections_level == "detailed"


@pytest.mark.asyncio
class TestMessageRepository:
    """Tests for MessageRepository."""

    async def test_create_message(self, session, user_data):
        """Test creating a message."""
        user_repo = UserRepository(session)
        message_repo = MessageRepository(session)

        user = await user_repo.create(**user_data)
        await session.commit()

        message = await message_repo.create(
            user_id=user.id,
            role="user",
            text="Ahoj, jak se máš?",
            transcript_raw="Ahoj, jak se máš?",
            correctness_score=85,
            words_total=4,
            words_correct=3
        )
        await session.commit()

        assert message.id is not None
        assert message.user_id == user.id
        assert message.role == "user"
        assert message.text == "Ahoj, jak se máš?"
        assert message.correctness_score == 85

    async def test_get_recent_messages(self, session, user_data):
        """Test getting recent messages."""
        user_repo = UserRepository(session)
        message_repo = MessageRepository(session)

        user = await user_repo.create(**user_data)
        await session.commit()

        # Create multiple messages
        for i in range(5):
            await message_repo.create(
                user_id=user.id,
                role="user",
                text=f"Message {i}"
            )
        await session.commit()

        messages = await message_repo.get_recent_by_user(user.id, limit=3)

        assert len(messages) == 3
        # Verify all messages are from the user
        assert all(m.user_id == user.id for m in messages)
        assert all(m.role == "user" for m in messages)


@pytest.mark.asyncio
class TestSavedWordRepository:
    """Tests for SavedWordRepository."""

    async def test_create_word(self, session, user_data):
        """Test saving a word."""
        user_repo = UserRepository(session)
        word_repo = SavedWordRepository(session)

        user = await user_repo.create(**user_data)
        await session.commit()

        word = await word_repo.create(
            user_id=user.id,
            word_czech="pivo",
            translation="пиво",
            context_sentence="Dáme si pivo?"
        )
        await session.commit()

        assert word.id is not None
        assert word.word_czech == "pivo"
        assert word.translation == "пиво"
        assert word.times_reviewed == 0

    async def test_get_user_words(self, session, user_data):
        """Test getting user's saved words."""
        user_repo = UserRepository(session)
        word_repo = SavedWordRepository(session)

        user = await user_repo.create(**user_data)
        await session.commit()

        # Create multiple words
        words_to_create = ["pivo", "knedlík", "ahoj"]
        for word in words_to_create:
            await word_repo.create(
                user_id=user.id,
                word_czech=word,
                translation=word
            )
        await session.commit()

        words = await word_repo.get_by_user(user.id)

        assert len(words) == 3

    async def test_delete_word(self, session, user_data):
        """Test deleting a saved word."""
        user_repo = UserRepository(session)
        word_repo = SavedWordRepository(session)

        user = await user_repo.create(**user_data)
        await session.commit()

        word = await word_repo.create(
            user_id=user.id,
            word_czech="test",
            translation="тест"
        )
        await session.commit()

        result = await word_repo.delete(word.id)

        assert result is True


@pytest.mark.asyncio
class TestStatsRepository:
    """Tests for StatsRepository."""

    async def test_get_or_create_daily_stats(self, session, user_data):
        """Test getting or creating daily stats."""
        user_repo = UserRepository(session)
        stats_repo = StatsRepository(session)

        user = await user_repo.create(**user_data)
        await session.commit()

        today = date.today()
        stats = await stats_repo.get_or_create_daily(user.id, today)
        await session.commit()

        assert stats.id is not None
        assert stats.user_id == user.id
        assert stats.date == today
        assert stats.messages_count == 0

    async def test_update_daily_stats(self, session, user_data):
        """Test updating daily stats."""
        user_repo = UserRepository(session)
        stats_repo = StatsRepository(session)

        user = await user_repo.create(**user_data)
        await session.commit()

        today = date.today()
        stats = await stats_repo.update_daily(
            user.id,
            today,
            messages_count=5,
            words_said=50,
            correct_percent=85,
            streak_day=3
        )
        await session.commit()

        assert stats.messages_count == 5
        assert stats.words_said == 50
        assert stats.correct_percent == 85
        assert stats.streak_day == 3

    async def test_get_user_stars(self, session, user_data):
        """Test getting user stars."""
        user_repo = UserRepository(session)
        stats_repo = StatsRepository(session)

        user = await user_repo.create(**user_data)
        await session.commit()

        stars = await stats_repo.get_user_stars(user.id)

        assert stars is not None
        assert stars.total == 0
        assert stars.available == 0
        assert stars.lifetime == 0

    async def test_update_stars(self, session, user_data):
        """Test updating user stars."""
        user_repo = UserRepository(session)
        stats_repo = StatsRepository(session)

        user = await user_repo.create(**user_data)
        await session.commit()

        updated_stars = await stats_repo.update_stars(
            user.id,
            total=10,
            available=5,
            lifetime=10
        )

        assert updated_stars is not None
        assert updated_stars.total == 10
        assert updated_stars.available == 5
        assert updated_stars.lifetime == 10

