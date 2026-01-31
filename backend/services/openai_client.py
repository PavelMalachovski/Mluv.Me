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
import tiktoken
from typing import Any, BinaryIO

import structlog
from openai import AsyncOpenAI, RateLimitError, APIError, APITimeoutError

from backend.config import Settings

logger = structlog.get_logger(__name__)

# Model pricing per 1K tokens (as of Dec 2024)
MODEL_PRICING = {
    'gpt-4o': {'input': 0.005, 'output': 0.015},
    'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
    'whisper-1': {'per_minute': 0.006},
    'tts-1': {'per_1M_chars': 15.0},
}

# Token limits for context
TOKEN_LIMITS = {
    'gpt-4o': 128000,
    'gpt-3.5-turbo': 16385,
}


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

        # Lazy load tokenizer (initialized on first use)
        self._encoding = None

    @property
    def encoding(self):
        """Lazy load tiktoken encoder."""
        if self._encoding is None:
            try:
                self._encoding = tiktoken.encoding_for_model(self.settings.openai_model)
            except KeyError:
                # Fallback to cl100k_base if model not found
                self._encoding = tiktoken.get_encoding("cl100k_base")
        return self._encoding

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

    async def transcribe_audio_with_detection(
        self,
        audio_file: BinaryIO | bytes,
    ) -> dict[str, str]:
        """
        Транскрибировать аудио с автоопределением языка.

        Используется для определения, говорит ли пользователь на чешском
        или на другом языке (русский, украинский, английский и т.д.)

        Args:
            audio_file: Аудио файл (file-like объект или байты)

        Returns:
            dict: {"text": str, "language": str}
                - text: транскрибированный текст
                - language: определённый язык ("cs", "ru", "uk", "en" и т.д.)

        Raises:
            APIError: При ошибке API OpenAI
        """
        self.logger.info(
            "transcribing_audio_with_language_detection",
            model=self.settings.whisper_model,
        )

        # Конвертация в bytes для возможности retry
        if hasattr(audio_file, 'read'):
            audio_bytes = audio_file.read()
            if hasattr(audio_file, 'seek'):
                audio_file.seek(0)
        else:
            audio_bytes = audio_file

        async def _transcribe():
            # Создаём новый BytesIO для каждой попытки (важно для retry!)
            file_obj = io.BytesIO(audio_bytes)
            file_obj.name = 'audio.ogg'

            # Без параметра language - Whisper автоматически определит язык
            # verbose_json возвращает дополнительную информацию включая язык
            transcript = await self.client.audio.transcriptions.create(
                model=self.settings.whisper_model,
                file=file_obj,
                response_format="verbose_json",  # Включает detected language
            )

            # Обработка разных форматов ответа
            if hasattr(transcript, 'text'):
                text = transcript.text
                language = getattr(transcript, 'language', 'cs') or 'cs'
            elif isinstance(transcript, dict):
                text = transcript.get('text', '')
                language = transcript.get('language', 'cs') or 'cs'
            else:
                text = str(transcript)
                language = 'cs'

            return {
                "text": text,
                "language": language,
            }

        try:
            result = await self._call_with_retry(_transcribe)
            self.logger.info(
                "transcription_with_detection_success",
                text_length=len(result["text"]),
                detected_language=result["language"],
            )
            return result
        except Exception as e:
            self.logger.error(
                "transcription_with_detection_failed",
                error=str(e),
            )
            raise

    async def generate_chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        json_mode: bool = False,
        model: str | None = None,
        stream: bool = False,
    ) -> str:
        """
        Сгенерировать ответ от GPT модели.

        Args:
            messages: Список сообщений в формате OpenAI
            temperature: Температура генерации (если None, используется из настроек)
            json_mode: Использовать JSON mode для структурированных ответов
            model: Модель для использования (если None, используется из настроек)
            stream: Использовать streaming (не совместимо с json_mode)

        Returns:
            str: Ответ от модели (JSON строка если json_mode=True)

        Raises:
            APIError: При ошибке API OpenAI
        """
        if temperature is None:
            temperature = self.settings.openai_temperature

        if model is None:
            model = self.settings.openai_model

        # Streaming не поддерживается с JSON mode
        if stream and json_mode:
            self.logger.warning("stream_with_json_mode_not_supported")
            stream = False

        self.logger.info(
            "generating_completion",
            model=model,
            temperature=temperature,
            json_mode=json_mode,
            stream=stream,
            messages_count=len(messages),
        )

        async def _complete():
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream,
            }

            if json_mode:
                params["response_format"] = {"type": "json_object"}

            if stream:
                # Streaming response
                full_response = ""
                response_stream = await self.client.chat.completions.create(**params)
                async for chunk in response_stream:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                return full_response
            else:
                # Regular response
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
        # Улучшенный маппинг скоростей для лучшего восприятия
        # Диапазон OpenAI TTS: 0.25 - 4.0, где 1.0 = нормальная скорость
        speed_map = {
            "very_slow": 0.6,   # Очень медленно для начинающих (было 0.75)
            "slow": 0.8,        # Медленно (было 0.9)
            "normal": 1.0,      # Нормальная скорость
            "native": 1.2,      # Быстрее для продвинутых (было 1.1)
        }
        return speed_map.get(speed_setting, 1.0)

    def get_optimal_model(
        self,
        czech_level: str,
        task_type: str = "analysis",
        fast_mode: bool = False,
    ) -> str:
        """
        Выбрать оптимальную модель в зависимости от уровня пользователя.

        Стратегия для ускорения в 2 раза:
        - fast_mode=True: всегда GPT-4o-mini (2x быстрее)
        - Для начинающих (beginner, intermediate): GPT-4o-mini
        - Для продвинутых (advanced, native): GPT-4o

        Args:
            czech_level: Уровень чешского (beginner, intermediate, advanced, native)
            task_type: Тип задачи (analysis, summarization)
            fast_mode: Режим быстрого ответа (всегда использует mini)

        Returns:
            str: Название модели
        """
        if not self.settings.use_adaptive_model_selection:
            return self.settings.openai_model

        # Для суммаризации всегда используем дешевую модель
        if task_type == "summarization":
            return self.settings.openai_model_simple

        # Fast mode - всегда GPT-4o-mini (2x быстрее!)
        if fast_mode:
            self.logger.info(
                "using_fast_mode_model",
                model=self.settings.openai_model_fast,
                level=czech_level,
            )
            return self.settings.openai_model_fast

        # Для начинающих и средних используем GPT-4o-mini (2x быстрее)
        if czech_level in ["beginner", "intermediate"]:
            self.logger.info(
                "using_fast_model_for_level",
                model=self.settings.openai_model_fast,
                level=czech_level,
            )
            return self.settings.openai_model_fast

        # Для продвинутых используем GPT-4o
        return self.settings.openai_model

    def estimate_tokens(self, text: str) -> int:
        """
        Оценить количество токенов в тексте.

        Args:
            text: Текст для оценки

        Returns:
            int: Приблизительное количество токенов
        """
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            self.logger.warning("token_estimation_failed", error=str(e))
            # Fallback: примерно 4 символа на токен
            return len(text) // 4

    def estimate_messages_tokens(self, messages: list[dict[str, str]]) -> int:
        """
        Оценить количество токенов в списке сообщений.

        Args:
            messages: Список сообщений OpenAI формата

        Returns:
            int: Приблизительное количество токенов
        """
        total_tokens = 0
        for message in messages:
            # 4 токена на сообщение (метаданные)
            total_tokens += 4
            for key, value in message.items():
                total_tokens += self.estimate_tokens(str(value))
        return total_tokens

    def optimize_conversation_history(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = 1500,
    ) -> list[dict[str, str]]:
        """
        Оптимизировать историю разговора для уменьшения использования токенов.

        Стратегия:
        - Всегда сохранять системный промпт
        - Всегда сохранять последние 3 сообщения
        - Если превышен лимит, обрезать более старые сообщения

        Args:
            messages: Список сообщений
            max_tokens: Максимальное количество токенов

        Returns:
            list: Оптимизированный список сообщений
        """
        if not messages:
            return messages

        current_tokens = self.estimate_messages_tokens(messages)

        if current_tokens <= max_tokens:
            return messages

        self.logger.info(
            "optimizing_conversation_history",
            original_tokens=current_tokens,
            max_tokens=max_tokens,
            messages_count=len(messages),
        )

        # Разделяем сообщения
        system_messages = [m for m in messages if m.get("role") == "system"]
        conversation = [m for m in messages if m.get("role") != "system"]

        # Всегда сохраняем последние 3 сообщения
        recent_messages = conversation[-3:] if len(conversation) >= 3 else conversation
        older_messages = conversation[:-3] if len(conversation) > 3 else []

        # Собираем оптимизированный список
        optimized = system_messages + recent_messages

        # Если все еще превышаем лимит, добавляем старые сообщения по одному
        if older_messages:
            for msg in reversed(older_messages):
                test_messages = system_messages + [msg] + recent_messages
                if self.estimate_messages_tokens(test_messages) <= max_tokens:
                    optimized = test_messages
                else:
                    break

        optimized_tokens = self.estimate_messages_tokens(optimized)

        self.logger.info(
            "conversation_history_optimized",
            original_tokens=current_tokens,
            optimized_tokens=optimized_tokens,
            reduction_percent=round((1 - optimized_tokens / current_tokens) * 100, 1),
            original_messages=len(messages),
            optimized_messages=len(optimized),
        )

        return optimized

    async def summarize_older_messages(
        self,
        messages: list[dict[str, str]],
    ) -> dict[str, str]:
        """
        Суммировать старые сообщения используя GPT-3.5-turbo для экономии.

        Args:
            messages: Список сообщений для суммаризации

        Returns:
            dict: Системное сообщение с суммарией
        """
        if not messages:
            return {"role": "system", "content": "Žádná předchozí historie."}

        # Форматируем сообщения для суммаризации
        formatted = []
        for msg in messages:
            role = "Student" if msg.get("role") == "user" else "Honzík"
            formatted.append(f"{role}: {msg.get('content', '')}")

        history_text = "\n".join(formatted)

        summary_prompt = f"""Shrň následující konverzaci mezi studentem češtiny a Honzíkem ve 2-3 větách.
Zaměř se na hlavní témata a chyby studenta:

{history_text}

Shrnutí:"""

        try:
            # Используем GPT-3.5-turbo для суммаризации (дешевле)
            summary = await self.generate_chat_completion(
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=0.3,
                model=self.settings.openai_model_simple,
            )

            self.logger.info(
                "messages_summarized",
                original_messages=len(messages),
                summary_length=len(summary),
            )

            return {
                "role": "system",
                "content": f"Předchozí konverzace (shrnutí): {summary}"
            }
        except Exception as e:
            self.logger.error("summarization_failed", error=str(e))
            return {"role": "system", "content": "Předchozí konverzace nebyla dostupná."}


