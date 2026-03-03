"""
Celery tasks for AI operations (OpenAI API calls).

These tasks offload heavy AI work to the Celery queue with rate limiting,
preventing OpenAI 429 errors when many users are active simultaneously.

Usage:
    # Fire-and-forget TTS generation
    generate_tts_audio.delay(text="Ahoj!", voice="alloy", speed=1.0, user_id=123)

    # Deferred AI response (e.g., for batch processing)
    result = generate_ai_response.apply_async(
        args=[messages, "gpt-4o-mini", 0.8],
        queue="ai",
    )
"""

import asyncio
from typing import Any


from backend.tasks.celery_app import celery_app


def _run_async(coro):
    """Run an async coroutine in a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    name="backend.tasks.ai_tasks.generate_ai_response",
    rate_limit="30/m",
    max_retries=3,
    default_retry_delay=5,
    soft_time_limit=60,
    time_limit=90,
    acks_late=True,
)
def generate_ai_response(
    messages: list[dict[str, str]],
    model: str = "gpt-4o-mini",
    temperature: float = 0.8,
    json_mode: bool = False,
    max_tokens: int | None = None,
) -> str:
    """
    Generate an AI chat completion via Celery queue.

    Rate limited to 30 requests/minute to prevent OpenAI 429 errors.

    Args:
        messages: OpenAI message format list
        model: Model name (gpt-4o, gpt-4o-mini)
        temperature: Response creativity (0.0-2.0)
        json_mode: Return JSON-structured response
        max_tokens: Max response tokens

    Returns:
        str: AI response text
    """
    from openai import OpenAI

    from backend.config import get_settings

    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)

    params: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if json_mode:
        params["response_format"] = {"type": "json_object"}
    if max_tokens is not None:
        params["max_tokens"] = max_tokens

    response = client.chat.completions.create(**params)
    return response.choices[0].message.content or ""


@celery_app.task(
    name="backend.tasks.ai_tasks.generate_tts_audio",
    rate_limit="20/m",
    max_retries=2,
    default_retry_delay=3,
    soft_time_limit=30,
    time_limit=45,
    acks_late=True,
)
def generate_tts_audio(
    text: str,
    voice: str = "alloy",
    speed: float = 1.0,
    user_id: int | None = None,
) -> dict[str, Any]:
    """
    Generate TTS audio via Celery queue and cache it in Redis.

    Rate limited to 20 requests/minute.

    Args:
        text: Text to synthesize
        voice: TTS voice name
        speed: Speech speed (0.25-4.0)
        user_id: Optional user ID for logging

    Returns:
        dict: {"cached": bool, "audio_size": int, "cache_key": str}
    """
    from openai import OpenAI

    from backend.config import get_settings

    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)

    # Generate TTS
    response = client.audio.speech.create(
        model=settings.tts_model,
        voice=voice,
        input=text,
        speed=speed,
    )
    audio_bytes = response.content

    # Cache in Redis (async operation run in sync context)
    async def _cache():
        from backend.cache.redis_client import redis_client
        from backend.services.cache_service import cache_service

        if not redis_client.is_connected:
            await redis_client.connect()
        await cache_service.cache_tts(text, voice, speed, audio_bytes)

    try:
        _run_async(_cache())
    except Exception:
        pass  # Caching failure is non-critical

    return {
        "audio_size": len(audio_bytes),
        "voice": voice,
        "user_id": user_id,
    }
