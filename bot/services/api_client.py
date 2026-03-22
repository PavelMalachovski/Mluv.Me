"""
API клиент для общения с backend.
"""

import base64
import io
from typing import Any, Optional

import aiohttp
import structlog
from aiohttp import FormData, ClientTimeout

logger = structlog.get_logger()

# Default timeout: 30s total, 10s connect
_DEFAULT_TIMEOUT = ClientTimeout(total=30, connect=10)


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
        self.session = aiohttp.ClientSession(timeout=_DEFAULT_TIMEOUT)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрыть сессию при выходе из контекста."""
        if self.session:
            await self.session.close()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Получить или создать сессию."""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=_DEFAULT_TIMEOUT)
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
            async with session.post(f"{self.base_url}/api/v1/users", json=data) as resp:
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
            logger.error("update_settings_error", telegram_id=telegram_id, error=str(e))
            return None

    async def process_voice(
        self,
        user_id: int,
        audio_bytes: bytes,
        filename: str = "voice.ogg",
        include_audio: bool = True,
    ) -> Optional[dict[str, Any]]:
        """
        Обработать голосовое сообщение.

        Args:
            user_id: Telegram ID пользователя
            audio_bytes: Байты аудио файла
            filename: Имя файла
            include_audio: Генерировать ли TTS аудио (False = только анализ)

        Returns:
            Результат обработки (transcript, corrections, audio_response, score)
        """
        session = await self._get_session()
        try:
            # Создаем multipart form data
            data = FormData()
            data.add_field("user_id", str(user_id))
            data.add_field("include_audio", str(include_audio).lower())
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

    async def generate_tts(self, user_id: int, text: str) -> Optional[bytes]:
        """
        Сгенерировать TTS аудио для готового текста.

        Args:
            user_id: Telegram ID пользователя
            text: Текст для озвучивания

        Returns:
            bytes аудио или None при ошибке
        """
        session = await self._get_session()
        try:
            data = FormData()
            data.add_field("user_id", str(user_id))
            data.add_field("text", text)

            async with session.post(
                f"{self.base_url}/api/v1/lessons/tts", data=data, timeout=30
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    audio_b64 = result.get("audio")
                    if audio_b64:
                        return base64.b64decode(audio_b64)
                else:
                    logger.error(
                        "generate_tts_failed",
                        user_id=user_id,
                        status=resp.status,
                    )
                return None
        except Exception as e:
            logger.error("generate_tts_error", user_id=user_id, error=str(e))
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
            logger.error("get_saved_words_error", telegram_id=telegram_id, error=str(e))
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
                "delete_conversation_history_error",
                telegram_id=telegram_id,
                error=str(e),
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

    async def full_reset_user(self, telegram_id: int) -> bool:
        """
        Полный сброс прогресса пользователя.

        Args:
            telegram_id: Telegram ID

        Returns:
            True если успешно
        """
        session = await self._get_session()
        try:
            async with session.delete(
                f"{self.base_url}/api/v1/users/telegram/{telegram_id}/full-reset"
            ) as resp:
                return resp.status == 200
        except Exception as e:
            logger.error("full_reset_user_error", telegram_id=telegram_id, error=str(e))
            return False

    async def close(self):
        """Закрыть сессию."""
        if self.session:
            await self.session.close()
            self.session = None

    # ──────────── Subscription / Payments ────────────

    async def activate_subscription(
        self,
        telegram_id: int,
        product_id: str,
        charge_id: str,
    ) -> Optional[dict[str, Any]]:
        """
        Activate Pro subscription after successful Telegram Stars payment.

        Args:
            telegram_id: Telegram user ID
            product_id: Product ID (pro_7d, pro_30d)
            charge_id: Telegram payment charge ID

        Returns:
            Result dict with success flag and expiry date
        """
        session = await self._get_session()
        try:
            payload = {
                "telegram_id": telegram_id,
                "product_id": product_id,
                "telegram_payment_charge_id": charge_id,
            }
            async with session.post(
                f"{self.base_url}/api/v1/subscription/activate-stars",
                json=payload,
                timeout=15,
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    error_body = await resp.text()
                    logger.error(
                        "activate_subscription_failed",
                        telegram_id=telegram_id,
                        status=resp.status,
                        body=error_body[:200],
                    )
                    return {"success": False, "error": error_body[:200]}
        except Exception as e:
            logger.error(
                "activate_subscription_error",
                telegram_id=telegram_id,
                error=str(e),
            )
            return None

    async def check_quota(
        self,
        telegram_id: int,
        msg_type: str = "text",
    ) -> Optional[dict[str, Any]]:
        """
        Check if user can send a message (quota check).

        Args:
            telegram_id: Telegram user ID
            msg_type: 'text' or 'voice'

        Returns:
            Quota info dict {allowed, plan, used, limit, remaining}
        """
        session = await self._get_session()
        try:
            async with session.get(
                f"{self.base_url}/api/v1/subscription/quota/{telegram_id}",
                params={"msg_type": msg_type},
                timeout=10,
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None
        except Exception as e:
            logger.error(
                "check_quota_error",
                telegram_id=telegram_id,
                error=str(e),
            )
            return None

    # ──────────── Star Shop ────────────

    async def get_star_shop(
        self, telegram_id: int
    ) -> Optional[dict[str, Any]]:
        """Get the star shop catalog for users."""
        session = await self._get_session()
        try:
            async with session.get(
                f"{self.base_url}/api/v1/star-shop/catalog",
                params={"telegram_id": telegram_id},
                timeout=10,
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None
        except Exception as e:
            logger.error("star_shop_catalog_error", error=str(e))
            return None

    async def buy_streak_shield(
        self, telegram_id: int
    ) -> Optional[dict[str, Any]]:
        """Buy a streak shield (100 stars)."""
        session = await self._get_session()
        try:
            async with session.post(
                f"{self.base_url}/api/v1/star-shop/streak-shield",
                params={"telegram_id": telegram_id},
                timeout=10,
            ) as resp:
                return await resp.json()
        except Exception as e:
            logger.error("buy_streak_shield_error", error=str(e))
            return None

    async def buy_trial_premium(
        self, telegram_id: int
    ) -> Optional[dict[str, Any]]:
        """Buy 1 day Pro access (500 stars)."""
        session = await self._get_session()
        try:
            async with session.post(
                f"{self.base_url}/api/v1/star-shop/trial-premium",
                params={"telegram_id": telegram_id},
                timeout=10,
            ) as resp:
                return await resp.json()
        except Exception as e:
            logger.error("buy_trial_premium_error", error=str(e))
            return None

    async def unlock_scenario(
        self, telegram_id: int, scenario_id: str
    ) -> Optional[dict[str, Any]]:
        """Unlock a premium scenario with stars."""
        session = await self._get_session()
        try:
            async with session.post(
                f"{self.base_url}/api/v1/star-shop/unlock-scenario",
                params={"telegram_id": telegram_id},
                json={"scenario_id": scenario_id},
                timeout=10,
            ) as resp:
                return await resp.json()
        except Exception as e:
            logger.error("unlock_scenario_error", error=str(e))
            return None
