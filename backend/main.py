"""
Main FastAPI application entry point.
Initializes the application, middleware, and routes.
"""
import sys
import asyncio

# Windows-specific: Ensure ProactorEventLoop is used for subprocess compatibility
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from typing import Optional, Dict, Any
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn

# Use relative imports for script compatibility
from .config import settings
from backend.routes.api_routes import router as api_router
from backend.routes.linkedin_jobs_routes import router as linkedin_jobs_router
from backend.routes.agent_routes import router as agent_router
from backend.routes.ats_routes import router as ats_router
from backend.routes.cover_letter_routes import router as cover_letter_router
from backend.api.autoagenthire import router as autoagenthire_router
from backend.routes.v2_routes import router as v2_router
from backend.database.connection import init_db
# from backend.utils.logger import setup_logger

# Setup logger
# logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    print(f"🚀 Starting {settings.APP_NAME}...")
    print(f"📝 Environment: {settings.APP_ENV}")
    print(f"🔧 Debug mode: {settings.DEBUG}")
    
    # Initialize database
    init_db()
    print("✓ Database initialized")
    
    # TODO: Initialize vector store
    # TODO: Start background scheduler
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    # TODO: Close database connections
    # TODO: Clean up resources


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Autonomous AI agent system for job discovery and applications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    debug=settings.DEBUG,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return a frontend-friendly error payload for 422 validation errors."""
    errors = []
    for e in exc.errors():
        loc = e.get("loc", [])
        field = ".".join(str(p) for p in loc if p not in ("body", "query", "path")) or ".".join(str(p) for p in loc)
        msg = e.get("msg", "Invalid request")
        errors.append(f"{field}: {msg}" if field else msg)

    return JSONResponse(
        status_code=422,
        content={
            "message": "Request validation failed",
            "errors": errors,
            "detail": exc.errors(),
        },
    )

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list if hasattr(settings, 'cors_origins_list') else settings.CORS_ORIGINS.split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip Middleware for response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(api_router)
app.include_router(linkedin_jobs_router)
app.include_router(agent_router)
app.include_router(ats_router)
app.include_router(cover_letter_router)
app.include_router(autoagenthire_router)
app.include_router(v2_router)  # V2 API for frontend


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "name": settings.APP_NAME,
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.APP_ENV,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Check actual DB connection
        "vector_db": "connected",  # TODO: Check vector DB connection
    }


"""NOTE: API endpoints are defined in routers under `backend/routes/`.

Historically this file also defined `/api/run-agent` and `/api/agent/status` directly.
Those duplicates caused contract confusion (JSON vs multipart) and route precedence
issues. The canonical endpoints live in `backend.routes.api_routes` (mounted above)
and in `backend.api.autoagenthire` via `register_autoagenthire_routes(app)`.
"""


# Include AutoAgentHire routes
try:
    from backend.api.autoagenthire import register_autoagenthire_routes
    register_autoagenthire_routes(app)
except Exception as e:
    print(f"⚠️  Could not load AutoAgentHire routes: {e}")

# TODO: Include routers
# app.include_router(routes.auth_router, prefix="/auth", tags=["Authentication"])
# app.include_router(routes.jobs_router, prefix="/jobs", tags=["Jobs"])
# app.include_router(routes.applications_router, prefix="/applications", tags=["Applications"])
# app.include_router(routes.user_router, prefix="/users", tags=["Users"])


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
