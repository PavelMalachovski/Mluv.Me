"""
Main FastAPI application.
Точка входа для backend API на Railway.com.
"""

import logging
import structlog
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
import httpx

from backend.config import get_settings
from backend.db.database import close_db
from backend.cache.redis_client import redis_client
from backend.routers import users, lesson, stats, words, web_auth, web_lessons, gamification, messages, scenarios, games, grammar

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

    # Create reusable HTTP client for frontend proxy
    app.state.http_client = httpx.AsyncClient(follow_redirects=True, timeout=30.0)

    yield

    # Shutdown
    logger.info("application_shutdown")
    await app.state.http_client.aclose()
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

# CORS middleware - restrict origins in production
_settings = get_settings()
_allowed_origins = (
    ["*"] if _settings.is_development
    else ["https://mluv.me", "https://www.mluv.me", "https://t.me"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(lesson.router)
app.include_router(stats.router)
app.include_router(words.router)
app.include_router(web_auth.router)
app.include_router(web_lessons.router)
app.include_router(gamification.router)
app.include_router(messages.router)
app.include_router(scenarios.router)
app.include_router(games.router)
app.include_router(grammar.router)


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
    "/api",
    status_code=status.HTTP_200_OK,
    summary="API Root endpoint",
    description="Корневой API endpoint",
    tags=["root"],
)
async def api_root() -> JSONResponse:
    """
    API Root endpoint.

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


# Error handlers (must be before catch-all route)
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


# Proxy all non-API requests to Next.js frontend (MUST BE LAST!)
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_to_frontend(request: Request, path: str):
    """
    Proxy all non-API requests to Next.js frontend.
    This allows Railway to serve both backend and frontend from the same URL.
    """
    # Skip API routes and special paths - these are already handled by registered routers
    # If we get here for an API path, it means no router matched, so return proper 404
    if path.startswith("api/"):
        return JSONResponse(
            status_code=404,
            content={"detail": f"API endpoint not found: /{path}"}
        )

    if path in ["docs", "redoc", "health", "openapi.json"] or path.startswith("docs") or path.startswith("redoc"):
        # These are handled by FastAPI directly, but if we somehow get here, skip proxy
        return JSONResponse(
            status_code=404,
            content={"detail": "Not found"}
        )

    # Proxy to Next.js
    settings = get_settings()
    frontend_url = f"http://localhost:{settings.frontend_port}/{path}"

    # Add query params
    if request.url.query:
        frontend_url += f"?{request.url.query}"

    # Use reusable HTTP client from app state
    client = request.app.state.http_client
    try:
        # Forward the request to Next.js
        response = await client.request(
            method=request.method,
            url=frontend_url,
            headers={
                key: value for key, value in request.headers.items()
                if key.lower() not in ["host", "connection"]
            },
            content=await request.body() if request.method in ["POST", "PUT", "PATCH"] else None,
        )

        # Filter headers to avoid conflicts
        headers = {
            key: value for key, value in response.headers.items()
            if key.lower() not in ["content-encoding", "content-length", "transfer-encoding", "connection"]
        }

        # Return appropriate response based on content type
        content_type = response.headers.get("content-type", "")

        if "text/html" in content_type or "text/css" in content_type or "application/javascript" in content_type:
            return HTMLResponse(
                content=response.text,
                status_code=response.status_code,
                headers=headers
            )
        elif "application/json" in content_type:
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code,
                headers=headers
            )
        else:
            # Stream binary content (images, fonts, etc.)
            return StreamingResponse(
                iter([response.content]),
                status_code=response.status_code,
                headers=headers,
                media_type=content_type
            )

    except httpx.RequestError as e:
        logger.warning("frontend_proxy_failed", path=path, error=str(e))
        # If Next.js is not available, return API info
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Mluv.Me - Loading...</title>
                <meta charset="utf-8">
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                    }
                    .container {
                        text-align: center;
                    }
                    h1 { font-size: 3em; margin-bottom: 0.2em; }
                    p { font-size: 1.2em; opacity: 0.9; }
                    .spinner {
                        border: 4px solid rgba(255,255,255,0.3);
                        border-radius: 50%;
                        border-top: 4px solid white;
                        width: 40px;
                        height: 40px;
                        animation: spin 1s linear infinite;
                        margin: 20px auto;
                    }
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🇨🇿 Mluv.Me</h1>
                    <div class="spinner"></div>
                    <p>Frontend is starting up...</p>
                    <p><small>API: <a href="/docs" style="color: white;">/docs</a></small></p>
                </div>
                <script>
                    setTimeout(() => window.location.reload(), 3000);
                </script>
            </body>
            </html>
            """,
            status_code=503
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

