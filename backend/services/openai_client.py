"""
OpenAI Client для интеграции с GPT-4o, Whisper (STT) и TTS API.

Реализует:
- Speech-to-Text (Whisper) для чешского языка
- Text-to-Speech (TTS) с мужским голосом
- LLM интеграция (GPT-4o) с JSON mode
- Exponential backoff при ошибках
- Rate limiting
"""

import asyncio
import io
from typing import Any, BinaryIO

import structlog
from openai import AsyncOpenAI, RateLimitError, APIError, APITimeoutError

from backend.config import Settings

logger = structlog.get_logger(__name__)


class OpenAIClient:
    """
    Обёртка над OpenAI API для работы с STT, LLM и TTS.

    Attributes:
        client: Асинхронный клиент OpenAI
        settings: Настройки приложения
    """

    def __init__(self, settings: Settings):
        """
        Инициализация OpenAI клиента.

        Args:
            settings: Настройки приложения с API ключом
        """
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.settings = settings
        self.logger = logger.bind(service="openai_client")

    async def _call_with_retry(
        self,
        func,
        max_retries: int = 3,
        initial_delay: float = 1.0,
    ) -> Any:
        """
        Вызов функции с exponential backoff при ошибках.

        Args:
            func: Асинхронная функция для вызова
            max_retries: Максимальное количество попыток
            initial_delay: Начальная задержка в секундах

        Returns:
            Результат вызова функции

        Raises:
            APIError: При исчерпании попыток или критической ошибке
        """
        delay = initial_delay

        for attempt in range(max_retries):
            try:
                return await func()
            except RateLimitError as e:
                if attempt == max_retries - 1:
                    self.logger.error(
                        "rate_limit_exceeded",
                        attempt=attempt + 1,
                        max_retries=max_retries,
                        error=str(e),
                    )
                    raise

                self.logger.warning(
                    "rate_limit_retry",
                    attempt=attempt + 1,
                    delay=delay,
                )
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff

            except APITimeoutError as e:
                if attempt == max_retries - 1:
                    self.logger.error(
                        "api_timeout",
                        attempt=attempt + 1,
                        max_retries=max_retries,
                        error=str(e),
                    )
                    raise

                self.logger.warning(
                    "timeout_retry",
                    attempt=attempt + 1,
                    delay=delay,
                )
                await asyncio.sleep(delay)
                delay *= 2

            except APIError as e:
                self.logger.error(
                    "api_error",
                    attempt=attempt + 1,
                    error=str(e),
                )
                raise

        raise APIError("Max retries exceeded")

    async def transcribe_audio(
        self,
        audio_file: BinaryIO | bytes,
        language: str = "cs",
    ) -> str:
        """
        Транскрибировать аудио в текст с помощью Whisper API.

        Args:
            audio_file: Аудио файл (file-like объект или байты)
            language: Язык аудио (по умолчанию чешский - 'cs')

        Returns:
            str: Транскрибированный текст

        Raises:
            APIError: При ошибке API OpenAI
        """
        self.logger.info(
            "transcribing_audio",
            language=language,
            model=self.settings.whisper_model,
        )

        # Конвертация bytes в file-like объект если нужно
        if isinstance(audio_file, bytes):
            audio_file = io.BytesIO(audio_file)

        async def _transcribe():
            # Whisper API требует file-like объект с атрибутом name
            if not hasattr(audio_file, 'name'):
                audio_file.name = 'audio.ogg'

            transcript = await self.client.audio.transcriptions.create(
                model=self.settings.whisper_model,
                file=audio_file,
                language=language,
            )
            return transcript.text

        try:
            text = await self._call_with_retry(_transcribe)
            self.logger.info(
                "transcription_success",
                text_length=len(text),
            )
            return text
        except Exception as e:
            self.logger.error(
                "transcription_failed",
                error=str(e),
            )
            raise

    async def generate_chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        json_mode: bool = False,
    ) -> str:
        """
        Сгенерировать ответ от GPT-4o.

        Args:
            messages: Список сообщений в формате OpenAI
            temperature: Температура генерации (если None, используется из настроек)
            json_mode: Использовать JSON mode для структурированных ответов

        Returns:
            str: Ответ от модели (JSON строка если json_mode=True)

        Raises:
            APIError: При ошибке API OpenAI
        """
        if temperature is None:
            temperature = self.settings.openai_temperature

        self.logger.info(
            "generating_completion",
            model=self.settings.openai_model,
            temperature=temperature,
            json_mode=json_mode,
            messages_count=len(messages),
        )

        async def _complete():
            params = {
                "model": self.settings.openai_model,
                "messages": messages,
                "temperature": temperature,
            }

            if json_mode:
                params["response_format"] = {"type": "json_object"}

            response = await self.client.chat.completions.create(**params)
            return response.choices[0].message.content

        try:
            content = await self._call_with_retry(_complete)
            self.logger.info(
                "completion_success",
                response_length=len(content) if content else 0,
            )
            return content or ""
        except Exception as e:
            self.logger.error(
                "completion_failed",
                error=str(e),
            )
            raise

    async def generate_speech(
        self,
        text: str,
        voice: str | None = None,
        speed: float = 1.0,
    ) -> bytes:
        """
        Сгенерировать речь из текста с помощью TTS API.

        Args:
            text: Текст для озвучивания
            voice: Голос (alloy, echo, fable, onyx, nova, shimmer)
            speed: Скорость речи (0.25 - 4.0)

        Returns:
            bytes: Аудио файл в формате MP3

        Raises:
            APIError: При ошибке API OpenAI
        """
        if voice is None:
            voice = self.settings.tts_voice

        self.logger.info(
            "generating_speech",
            text_length=len(text),
            voice=voice,
            speed=speed,
            model=self.settings.tts_model,
        )

        async def _generate():
            response = await self.client.audio.speech.create(
                model=self.settings.tts_model,
                voice=voice,
                input=text,
                speed=speed,
            )
            # Читаем содержимое из response
            return response.content

        try:
            audio_content = await self._call_with_retry(_generate)
            self.logger.info(
                "speech_generation_success",
                audio_size_bytes=len(audio_content),
            )
            return audio_content
        except Exception as e:
            self.logger.error(
                "speech_generation_failed",
                error=str(e),
            )
            raise

    def get_voice_speed_mapping(self, speed_setting: str) -> float:
        """
        Конвертировать настройку скорости в числовое значение для TTS.

        Args:
            speed_setting: Настройка скорости (very_slow, slow, normal, native)

        Returns:
            float: Скорость для TTS API (0.25 - 4.0)
        """
        speed_map = {
            "very_slow": 0.75,
            "slow": 0.9,
            "normal": 1.0,
            "native": 1.1,
        }
        return speed_map.get(speed_setting, 1.0)


