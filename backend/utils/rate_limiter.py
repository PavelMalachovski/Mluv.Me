"""
Rate limiting and concurrency control for OpenAI API calls.

Prevents overwhelming OpenAI with too many concurrent requests,
which causes 429 errors and degrades response times.
"""

import asyncio
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog

logger = structlog.get_logger(__name__)


class OpenAIConcurrencyLimiter:
    """
    Limits concurrent OpenAI API calls using asyncio.Semaphore.

    At 100+ users, many requests can hit OpenAI simultaneously.
    This limiter ensures we stay within rate limits and avoid 429 errors.

    Usage:
        limiter = OpenAIConcurrencyLimiter(max_concurrent=10)

        async with limiter.acquire("chat"):
            response = await openai_client.chat(...)
    """

    def __init__(
        self,
        max_concurrent_chat: int = 10,
        max_concurrent_tts: int = 8,
        max_concurrent_stt: int = 8,
    ) -> None:
        self._chat_semaphore = asyncio.Semaphore(max_concurrent_chat)
        self._tts_semaphore = asyncio.Semaphore(max_concurrent_tts)
        self._stt_semaphore = asyncio.Semaphore(max_concurrent_stt)
        self._semaphores = {
            "chat": self._chat_semaphore,
            "tts": self._tts_semaphore,
            "stt": self._stt_semaphore,
        }

        # Metrics
        self._waiting_count: dict[str, int] = {"chat": 0, "tts": 0, "stt": 0}
        self._total_requests: dict[str, int] = {"chat": 0, "tts": 0, "stt": 0}
        self._total_wait_time: dict[str, float] = {"chat": 0.0, "tts": 0.0, "stt": 0.0}

    @asynccontextmanager
    async def acquire(self, request_type: str = "chat") -> AsyncGenerator[None, None]:
        """
        Acquire a slot for an OpenAI API call.

        Blocks if max concurrent calls are already in progress.

        Args:
            request_type: Type of request ("chat", "tts", "stt")
        """
        semaphore = self._semaphores.get(request_type, self._chat_semaphore)
        self._waiting_count[request_type] = self._waiting_count.get(request_type, 0) + 1
        self._total_requests[request_type] = (
            self._total_requests.get(request_type, 0) + 1
        )

        start = time.monotonic()

        try:
            await semaphore.acquire()
            wait_time = time.monotonic() - start
            self._total_wait_time[request_type] = (
                self._total_wait_time.get(request_type, 0.0) + wait_time
            )

            if wait_time > 0.1:  # Log only meaningful waits
                logger.info(
                    "openai_semaphore_acquired",
                    type=request_type,
                    wait_seconds=round(wait_time, 3),
                    waiting=self._waiting_count[request_type] - 1,
                )

            yield
        finally:
            semaphore.release()
            self._waiting_count[request_type] = max(
                0, self._waiting_count.get(request_type, 1) - 1
            )

    def get_stats(self) -> dict:
        """Get current limiter statistics."""
        stats = {}
        for req_type in ("chat", "tts", "stt"):
            sem = self._semaphores[req_type]
            total = self._total_requests.get(req_type, 0)
            stats[req_type] = {
                "available_slots": sem._value,
                "waiting": self._waiting_count.get(req_type, 0),
                "total_requests": total,
                "avg_wait_ms": round(
                    (self._total_wait_time.get(req_type, 0) / total * 1000)
                    if total > 0
                    else 0,
                    1,
                ),
            }
        return stats


# Global singleton
openai_limiter = OpenAIConcurrencyLimiter(
    max_concurrent_chat=10,
    max_concurrent_tts=8,
    max_concurrent_stt=8,
)
