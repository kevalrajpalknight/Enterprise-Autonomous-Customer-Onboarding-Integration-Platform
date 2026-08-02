from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from worker.config import settings

engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def fetch_document_storage_key(document_id: uuid.UUID) -> str:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT storage_key FROM documents WHERE id = :document_id"),
            {"document_id": document_id},
        )
        storage_key = result.scalar_one()
        return str(storage_key)


async def save_parsed_payload(document_id: uuid.UUID, payload: dict[str, Any]) -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("UPDATE documents SET parsed_payload = :payload::jsonb WHERE id = :document_id"),
            {"payload": json.dumps(payload), "document_id": document_id},
        )
        await session.commit()
