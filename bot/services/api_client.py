"""
API клиент для общения с backend.
"""

import io
from typing import Any, Optional

import aiohttp
import structlog
from aiohttp import FormData

logger = structlog.get_logger()


class APIClient:
    """HTTP клиент для общения с backend API."""

    def __init__(self, base_url: str):
        """
        Инициализация клиента.

        Args:
            base_url: Базовый URL backend API
        """
        self.base_url = base_url.rstrip("/")
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Создать сессию при входе в контекст."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрыть сессию при выходе из контекста."""
        if self.session:
            await self.session.close()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Получить или создать сессию."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session

    async def get_user(self, telegram_id: int) -> Optional[dict[str, Any]]:
        """
        Получить пользователя по Telegram ID.

        Args:
            telegram_id: Telegram ID пользователя

        Returns:
            Данные пользователя или None если не найден
        """
        session = await self._get_session()
        try:
            async with session.get(
                f"{self.base_url}/api/v1/users/telegram/{telegram_id}"
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                elif resp.status == 404:
                    return None
                else:
                    logger.error(
                        "get_user_failed",
                        telegram_id=telegram_id,
                        status=resp.status,
                    )
                    return None
        except Exception as e:
            logger.error("get_user_error", telegram_id=telegram_id, error=str(e))
            return None

    async def create_user(
        self,
        telegram_id: int,
        username: Optional[str],
        first_name: str,
        native_language: str,
        level: str,
    ) -> Optional[dict[str, Any]]:
        """
        Создать нового пользователя.

        Language Immersion: UI всегда на чешском, native_language для объяснений.

        Args:
            telegram_id: Telegram ID
            username: Username
            first_name: Имя
            native_language: Родной язык для объяснений (ru/uk/pl/sk)
            level: Уровень чешского

        Returns:
            Данные созданного пользователя
        """
        session = await self._get_session()
        try:
            data = {
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "native_language": native_language,
                "level": level,
            }
            async with session.post(
                f"{self.base_url}/api/v1/users", json=data
            ) as resp:
                if resp.status in [200, 201]:
                    return await resp.json()
                else:
                    logger.error(
                        "create_user_failed",
                        telegram_id=telegram_id,
                        status=resp.status,
                    )
                    return None
        except Exception as e:
            logger.error("create_user_error", telegram_id=telegram_id, error=str(e))
            return None

    async def update_user_settings(
        self, telegram_id: int, **settings
    ) -> Optional[dict[str, Any]]:
        """
        Обновить настройки пользователя.

        Args:
            telegram_id: Telegram ID
            **settings: Настройки для обновления

        Returns:
            Обновленные настройки
        """
        session = await self._get_session()
        try:
            async with session.patch(
                f"{self.base_url}/api/v1/users/telegram/{telegram_id}/settings",
                json=settings,
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.error(
                        "update_settings_failed",
                        telegram_id=telegram_id,
                        status=resp.status,
                    )
                    return None
        except Exception as e:
            logger.error(
                "update_settings_error", telegram_id=telegram_id, error=str(e)
            )
            return None

    async def process_voice(
        self, user_id: int, audio_bytes: bytes, filename: str = "voice.ogg"
    ) -> Optional[dict[str, Any]]:
        """
        Обработать голосовое сообщение.

        Args:
            user_id: Telegram ID пользователя
            audio_bytes: Байты аудио файла
            filename: Имя файла

        Returns:
            Результат обработки (transcript, corrections, audio_response, score)
        """
        session = await self._get_session()
        try:
            # Создаем multipart form data
            data = FormData()
            data.add_field("user_id", str(user_id))
            data.add_field(
                "audio",
                io.BytesIO(audio_bytes),
                filename=filename,
                content_type="audio/ogg",
            )

            async with session.post(
                f"{self.base_url}/api/v1/lessons/process", data=data, timeout=30
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.error(
                        "process_voice_failed",
                        user_id=user_id,
                        status=resp.status,
                    )
                    return None
        except Exception as e:
            logger.error("process_voice_error", user_id=user_id, error=str(e))
            return None

    async def process_text(
        self,
        user_id: int,
        text: str,
        include_audio: bool = True,
    ) -> Optional[dict[str, Any]]:
        """
        Обработать текстовое сообщение.

        В отличие от голосового:
        1. НЕТ этапа STT (текст уже есть)
        2. Опционально TTS (можно отключить для экономии)
        3. Быстрее на 1-2 секунды

        Args:
            user_id: Telegram ID пользователя
            text: Текст сообщения на чешском
            include_audio: Генерировать ли голосовой ответ

        Returns:
            Результат обработки (honzik_response, corrections, audio_response, score)
        """
        session = await self._get_session()
        try:
            # Создаем multipart form data
            data = FormData()
            data.add_field("user_id", str(user_id))
            data.add_field("text", text)
            data.add_field("include_audio", str(include_audio).lower())

            async with session.post(
                f"{self.base_url}/api/v1/lessons/process/text",
                data=data,
                timeout=30,
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    error_body = await resp.text()
                    logger.error(
                        "process_text_failed",
                        user_id=user_id,
                        status=resp.status,
                        body=error_body[:200],
                    )
                    return None
        except Exception as e:
            logger.error("process_text_error", user_id=user_id, error=str(e))
            return None

    async def get_stats(self, telegram_id: int) -> Optional[dict[str, Any]]:
        """
        Получить статистику пользователя.

        Args:
            telegram_id: Telegram ID

        Returns:
            Статистика пользователя
        """
        session = await self._get_session()
        try:
            async with session.get(
                f"{self.base_url}/api/v1/stats/{telegram_id}/summary"
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.error(
                        "get_stats_failed", telegram_id=telegram_id, status=resp.status
                    )
                    return None
        except Exception as e:
            logger.error("get_stats_error", telegram_id=telegram_id, error=str(e))
            return None

    async def get_saved_words(
        self, telegram_id: int, limit: int = 10
    ) -> Optional[list[dict[str, Any]]]:
        """
        Получить сохраненные слова.

        Args:
            telegram_id: Telegram ID
            limit: Максимальное количество слов

        Returns:
            Список сохраненных слов
        """
        session = await self._get_session()
        try:
            async with session.get(
                f"{self.base_url}/api/v1/words/{telegram_id}?limit={limit}"
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.error(
                        "get_saved_words_failed",
                        telegram_id=telegram_id,
                        status=resp.status,
                    )
                    return None
        except Exception as e:
            logger.error(
                "get_saved_words_error", telegram_id=telegram_id, error=str(e)
            )
            return None

    async def reset_conversation(self, telegram_id: int) -> bool:
        """
        Сбросить контекст разговора.

        Args:
            telegram_id: Telegram ID

        Returns:
            True если успешно
        """
        session = await self._get_session()
        try:
            async with session.post(
                f"{self.base_url}/api/v1/words/{telegram_id}/reset-context"
            ) as resp:
                return resp.status == 200
        except Exception as e:
            logger.error(
                "reset_conversation_error", telegram_id=telegram_id, error=str(e)
            )
            return False

    async def delete_conversation_history(self, telegram_id: int) -> bool:
        """
        Удалить всю историю переписки пользователя.

        Args:
            telegram_id: Telegram ID

        Returns:
            True если успешно
        """
        session = await self._get_session()
        try:
            async with session.delete(
                f"{self.base_url}/api/v1/messages/{telegram_id}/history"
            ) as resp:
                return resp.status == 200
        except Exception as e:
            logger.error(
                "delete_conversation_history_error", telegram_id=telegram_id, error=str(e)
            )
            return False

    async def translate_word(
        self, word: str, target_language: str = "ru"
    ) -> Optional[dict[str, Any]]:
        """
        Перевести слово с чешского на целевой язык.

        Args:
            word: Слово для перевода (чешское)
            target_language: Язык перевода (ru/uk)

        Returns:
            Результат перевода или None при ошибке
        """
        session = await self._get_session()
        try:
            data = {
                "word": word,
                "target_language": target_language,
            }
            async with session.post(
                f"{self.base_url}/api/v1/words/translate", json=data
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.error(
                        "translate_word_failed",
                        word=word,
                        target_language=target_language,
                        status=resp.status,
                    )
                    return None
        except Exception as e:
            logger.error(
                "translate_word_error",
                word=word,
                target_language=target_language,
                error=str(e),
            )
            return None

    async def close(self):
        """Закрыть сессию."""
        if self.session:
            await self.session.close()
            self.session = None

