from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter

from api.config import settings
from api.db.session import engine
from api.routers import documents

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    redis_conn = await aioredis.from_url(  # type: ignore[no-untyped-call]
        settings.redis_url, encoding="utf-8", decode_responses=True
    )
    await FastAPILimiter.init(redis_conn)
    logger.info("FastAPILimiter initialised against %s", settings.redis_url)
    yield
    await FastAPILimiter.close()
    await redis_conn.aclose()
    await engine.dispose()


app = FastAPI(
    title="OnboardAI Enterprise API",
    description=(
        "Enterprise-grade autonomous customer onboarding and integration platform. "
        "Provides document ingestion, AI-driven extraction, workflow orchestration, "
        "human-in-the-loop review, and production sync capabilities."
    ),
    version="1.0.0",
    contact={"name": "Keval Rajpal"},
    license_info={"name": "MIT"},
    openapi_tags=[
        {"name": "System", "description": "Health and liveness probes"},
        {
            "name": "Documents",
            "description": "Document upload and lifecycle management",
        },
    ],
    lifespan=lifespan,
)

# Lock down in production via ALLOWED_ORIGINS env var
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Error handlers ────────────────────────────────────────────────────────────


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors: list[dict[str, Any]] = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Request validation failed", "errors": errors},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, "headers", None) or {},
    )


# ── Routers ───────────────────────────────────────────────────────────────────

v1 = FastAPI(
    title="OnboardAI v1",
    description="Version 1 of the OnboardAI API.",
    version="1.0.0",
)
v1.include_router(documents.router)

app.mount("/v1", v1)


# ── System ────────────────────────────────────────────────────────────────────


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "api"}
