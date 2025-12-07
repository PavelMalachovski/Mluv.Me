"""
Main FastAPI application.
Точка входа для backend API на Railway.com.
"""

import logging
import structlog
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import get_settings
from backend.db.database import close_db
from backend.cache.redis_client import redis_client
from backend.routers import users, lesson, stats, words

# Configure structlog for Railway.com
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Lifespan context manager для FastAPI.
    Управляет startup и shutdown событиями.
    """
    settings = get_settings()

    # Startup
    logger.info(
        "application_startup",
        environment=settings.environment,
        port=settings.port,
    )

    # Connect to Redis
    try:
        await redis_client.connect()
    except Exception as e:
        logger.warning("redis_startup_failed", error=str(e))

    yield

    # Shutdown
    logger.info("application_shutdown")
    await redis_client.disconnect()
    await close_db()


# Create FastAPI app
app = FastAPI(
    title="Mluv.Me API",
    description="API для Telegram бота Хонзика - практика чешского языка",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not get_settings().is_production else None,
    redoc_url="/redoc" if not get_settings().is_production else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production можно ограничить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(lesson.router)
app.include_router(stats.router)
app.include_router(words.router)


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Health check endpoint для Railway.com",
    tags=["health"],
)
async def health_check() -> JSONResponse:
    """
    Health check endpoint.
    Railway.com использует этот endpoint для проверки работоспособности.

    Returns:
        JSONResponse: Статус приложения
    """
    settings = get_settings()

    # Check Redis connection
    redis_status = "unknown"
    if settings.cache_enabled:
        redis_status = "healthy" if await redis_client.ping() else "unavailable"
    else:
        redis_status = "disabled"

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "service": "mluv-me",
            "version": "1.0.0",
            "environment": settings.environment,
            "redis": redis_status,
        }
    )


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Root endpoint",
    description="Корневой endpoint",
    tags=["root"],
)
async def root() -> JSONResponse:
    """
    Root endpoint.

    Returns:
        JSONResponse: Приветствие от Хонзика
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Nazdar! 🇨🇿 Jsem Honzík - tvůj průvodce češtinou!",
            "description": "Mluv.Me API - практика чешского языка с AI",
            "docs": "/docs",
        }
    )


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """
    Global exception handler.
    Логирует все необработанные ошибки.
    """
    import traceback

    logger.error(
        "unhandled_exception",
        exc_type=type(exc).__name__,
        exc_message=str(exc),
        path=request.url.path,
        exc_info=True,
    )

    # В development режиме возвращаем traceback
    settings = get_settings()
    content = {
        "detail": "Internal server error",
        "message": "Něco se pokazilo, ale už to opravuji! 🔧"
    }

    if settings.is_development:
        content["error"] = str(exc)
        content["traceback"] = traceback.format_exc()

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content
    )


if __name__ == "__main__":
    import uvicorn
    import logging

    settings = get_settings()

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )

