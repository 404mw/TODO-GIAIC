"""FastAPI application entry point for Perpetua Flow Backend.

T370: Configure middleware order (request_id -> logging -> auth -> rate_limit)
T372: Implement FastAPI app factory
T373: Add startup/shutdown events for DB pool

This module creates and configures the FastAPI application with:
- CORS middleware
- Request ID middleware
- Logging middleware
- Metrics middleware
- Auth middleware
- Idempotency middleware
- Rate limiting
- API routes
- Error handlers
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.config import Settings, get_settings
from src.middleware.auth import AuthMiddleware
from src.middleware.error_handler import register_error_handlers
from src.middleware.idempotency import IdempotencyMiddleware
from src.middleware.logging import LoggingMiddleware
from src.middleware.metrics import MetricsMiddleware
from src.middleware.rate_limit import setup_rate_limiting
from src.middleware.request_id import RequestIDMiddleware
from src.middleware.security import SecurityHeadersMiddleware
from src.migrations import run_migrations

logger = logging.getLogger(__name__)

# Global database engine (initialized at startup)
_db_engine: AsyncEngine | None = None


async def init_database(settings: Settings) -> AsyncEngine:
    """Initialize the database connection pool.

    T373: Database pool initialization at startup.

    Args:
        settings: Application settings with database URL

    Returns:
        Configured async database engine
    """
    global _db_engine

    logger.info("Initializing database connection pool...")

    _db_engine = create_async_engine(
        settings.database_url.get_secret_value(),
        echo=settings.debug,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,  # Recycle connections after 1 hour
    )

    # Test connection
    async with _db_engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

    logger.info("Database connection pool initialized successfully")
    return _db_engine


async def close_database() -> None:
    """Close the database connection pool.

    T373: Database pool cleanup at shutdown.
    """
    global _db_engine

    if _db_engine is not None:
        logger.info("Closing database connection pool...")
        await _db_engine.dispose()
        _db_engine = None
        logger.info("Database connection pool closed")


def get_db_engine() -> AsyncEngine | None:
    """Get the global database engine.

    Returns:
        The database engine if initialized, None otherwise
    """
    return _db_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events.

    T373: Handles startup and shutdown tasks:
    - Database connection pool initialization
    - Background task scheduling
    - Cleanup on shutdown
    """
    settings = get_settings()

    # ==========================================================================
    # STARTUP
    # ==========================================================================
    logger.info(f"Starting Perpetua Flow Backend in {settings.environment} mode...")

    # Initialize database connection pool
    try:
        engine = await init_database(settings)
        app.state.db_engine = engine
        logger.info("Database engine attached to app state")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Run database migrations
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker

        async_session_maker = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session_maker() as session:
            await run_migrations(session)
    except Exception as e:
        logger.error(f"Failed to run database migrations: {e}")
        raise

    # Store settings in app state for middleware access
    app.state.settings = settings

    logger.info("Perpetua Flow Backend startup complete")

    yield

    # ==========================================================================
    # SHUTDOWN
    # ==========================================================================
    logger.info("Shutting down Perpetua Flow Backend...")

    # Close database connection pool
    await close_database()

    logger.info("Perpetua Flow Backend shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    T372: FastAPI app factory implementation.

    Returns:
        Configured FastAPI application instance
    """
    settings = get_settings()

    app = FastAPI(
        title="Perpetua Flow Backend API",
        description="Backend API for Perpetua Flow task management application.",
        version="1.0.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # ==========================================================================
    # RATE LIMITING (via slowapi)
    # ==========================================================================

    setup_rate_limiting(app)

    # ==========================================================================
    # ERROR HANDLERS (must be registered before middleware)
    # ==========================================================================

    register_error_handlers(app)

    # ==========================================================================
    # MIDDLEWARE
    # T370: Configure middleware order (request_id -> logging -> auth -> rate_limit)
    #
    # NOTE: In FastAPI/Starlette, middleware is processed in REVERSE order
    # of addition. The LAST middleware added is executed FIRST on incoming
    # requests and LAST on outgoing responses.
    #
    # Desired execution order on REQUEST:
    # 1. RequestIDMiddleware       - Generate/extract request ID
    # 2. SecurityHeadersMiddleware - Add security headers
    # 3. LoggingMiddleware         - Log request with request ID
    # 4. MetricsMiddleware         - Collect metrics
    # 5. AuthMiddleware            - Validate JWT token
    # 6. IdempotencyMiddleware     - Check for duplicate requests
    # 7. CORSMiddleware            - Handle CORS
    #
    # So we add them in REVERSE order:
    # ==========================================================================

    # 7. CORS middleware (added first = executed last on request)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[
            "X-Request-ID",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "X-Idempotent-Replayed",
        ],
    )

    # 6. Idempotency middleware (FR-059)
    app.add_middleware(IdempotencyMiddleware)

    # 5. Auth middleware (validate JWT tokens)
    app.add_middleware(AuthMiddleware)

    # 4. Metrics middleware (collect metrics for all requests)
    app.add_middleware(MetricsMiddleware)

    # 3. Logging middleware (log all requests with structured JSON)
    app.add_middleware(LoggingMiddleware)

    # 2. Security headers middleware (T411)
    app.add_middleware(SecurityHeadersMiddleware)

    # 1. Request ID middleware (added last = executed first on request)
    app.add_middleware(RequestIDMiddleware)

    # ==========================================================================
    # ROUTES
    # ==========================================================================

    # Health check routes (not under /api/v1 - always accessible)
    from src.api.health import router as health_router
    app.include_router(health_router)

    # API v1 routes (centralized router - T367, T368)
    from src.api.router import api_v1_router
    app.include_router(api_v1_router)

    # Mount JWKS at well-known path (outside /auth prefix)
    @app.get("/api/v1/.well-known/jwks.json", tags=["authentication"])
    async def jwks_well_known():
        """JWKS endpoint at well-known path."""
        from src.dependencies import get_jwt_manager, get_settings
        jwt_manager = get_jwt_manager(get_settings())
        return jwt_manager.get_jwks()

    return app


# Application instance for uvicorn
# Guarded to prevent failures when tests import this module
import sys as _sys

if "pytest" not in _sys.modules:
    app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level="debug" if settings.debug else "info",
    )
