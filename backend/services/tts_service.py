"""
TTS сервис с дедупликацией параллельных запросов и прогревом кеша.

Бот работает в два шага: сначала запрашивает анализ без аудио (быстро),
потом отдельным запросом просит озвучку. Чтобы озвучка не начиналась
только со второго запроса, эндпоинт /process прогревает её в фоне
сразу после генерации ответа Хонзика (prewarm_tts). Когда бот приходит
за аудио, оно уже готово или почти готово — /tts просто присоединяется
к той же задаче (get_or_generate_tts).
"""

import asyncio

import structlog

from backend.services.cache_service import cache_service
from backend.services.openai_client import OpenAIClient

logger = structlog.get_logger(__name__)

# In-flight генерации TTS: cache_key -> Task[bytes].
# Позволяет второму запросу на тот же текст дождаться уже запущенной
# генерации вместо повторного вызова OpenAI.
_inflight: dict[str, asyncio.Task] = {}

# Сильные ссылки на фоновые prewarm-задачи (event loop держит только weakref,
# без этого задача может быть собрана GC до завершения).
_background_tasks: set[asyncio.Task] = set()


async def get_or_generate_tts(
    openai_client: OpenAIClient,
    text: str,
    voice: str,
    speed: float,
) -> bytes:
    """
    Получить TTS аудио: из Redis-кеша, из уже запущенной генерации
    или сгенерировать заново (с записью в кеш).
    """
    cached = await cache_service.get_cached_tts(text, voice, speed)
    if cached:
        return cached

    cache_key = cache_service.create_tts_cache_key(text, voice, speed)

    existing = _inflight.get(cache_key)
    if existing is not None:
        logger.info("tts_joined_inflight", text_preview=text[:30])
        return await asyncio.shield(existing)

    async def _generate() -> bytes:
        try:
            audio = await openai_client.generate_speech(
                text=text, voice=voice, speed=speed, use_cache=False
            )
            await cache_service.cache_tts(text, voice, speed, audio)
            return audio
        finally:
            _inflight.pop(cache_key, None)

    task = asyncio.create_task(_generate())
    _inflight[cache_key] = task
    return await asyncio.shield(task)


def prewarm_tts(
    openai_client: OpenAIClient,
    text: str,
    voice: str,
    speed: float,
) -> None:
    """
    Запустить генерацию TTS в фоне (fire-and-forget), не дожидаясь результата.

    Вызывается из /process при include_audio=False: пока бот отправляет
    пользователю správnost, аудио уже генерируется и попадает в кеш.
    Ошибки логируются и не влияют на основной запрос.
    """

    async def _prewarm() -> None:
        try:
            await get_or_generate_tts(openai_client, text, voice, speed)
            logger.info("tts_prewarmed", text_preview=text[:30])
        except Exception as e:
            logger.warning("tts_prewarm_failed", error=str(e))

    task = asyncio.create_task(_prewarm())
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
