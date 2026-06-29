"""
Rewire — FastAPI application factory.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Rewire starting up", version=settings.app_version, env=settings.environment)

    # Validate DB connection
    try:
        from app.db.session import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            from sqlalchemy import text

            await session.execute(text("SELECT 1"))
        logger.info("PostgreSQL connection verified")
    except Exception as e:
        logger.error("PostgreSQL connection failed", error=str(e))

    # Validate Redis connection
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.redis_url)
        await r.ping()
        await r.aclose()
        logger.info("Redis connection verified")
    except Exception as e:
        logger.error("Redis connection failed", error=str(e))

    # Validate LLM connectivity
    if settings.openrouter_api_key:
        logger.info("LLM configured", model=settings.llm_model)
    else:
        logger.warning("No LLM API key configured — AI features will use fallbacks")

    yield

    logger.info("Rewire shutting down")


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title="Rewire API",
        description=(
            "AI Addiction Recovery Platform — Your second brain for defeating dopamine addiction.\n\n"
            "## Mission\n"
            "Destroy dopamine addiction by changing the environment rather than relying on willpower.\n\n"
            "## Authentication\n"
            "- Use `POST /api/v1/auth/register` to create an account.\n"
            "- Use `POST /api/v1/auth/login` to get a JWT access token.\n"
            "- Add `Authorization: Bearer <token>` to protected endpoints.\n\n"
            "## Core Features\n"
            "- **AI Coach** — Empathetic, action-oriented recovery coaching\n"
            "- **Smart Journal** — Context-rich craving tracking with AI responses\n"
            "- **Trigger Intelligence** — AI-discovered behavioral patterns\n"
            "- **Recovery Dashboard** — Real-time wellness & recovery metrics\n"
            "- **Emergency Mode** — Crisis intervention with coping tools\n"
            "- **Gamification** — XP, levels, badges, daily quests\n"
        ),
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        license_info={"name": "MIT"},
    )

    # ─── CORS ────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ─── Exception Handlers ───────────────────────────────────────────────────
    register_exception_handlers(app)

    # ─── Prometheus Metrics ───────────────────────────────────────────────────
    if settings.prometheus_enabled:
        try:
            from prometheus_fastapi_instrumentator import Instrumentator

            Instrumentator().instrument(app).expose(app, endpoint="/metrics")
        except ImportError:
            logger.warning("prometheus_fastapi_instrumentator not installed, skipping metrics")

    # ─── Routers ──────────────────────────────────────────────────────────────
    app.include_router(api_v1_router, prefix=settings.api_prefix)

    return app


app = create_app()
