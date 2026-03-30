"""
Audit service — list audit events for a workflow.
"""
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditEvent

logger = structlog.get_logger(__name__)


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_events(self, workflow_id: str) -> list[AuditEvent]:
        result = await self.db.execute(
            select(AuditEvent).where(AuditEvent.workflow_id == workflow_id)
        )
        return list(result.scalars().all())

    async def record_event(self, workflow_id: str, event_type: str, actor_id: str, payload: dict, correlation_id: str | None = None) -> None:
        event = AuditEvent(
            workflow_id=workflow_id,
            event_type=event_type,
            actor_id=actor_id,
            payload=payload,
            correlation_id=correlation_id,
        )
        self.db.add(event)
        await self.db.commit()
        logger.info("Audit event recorded", workflow_id=workflow_id, type=event_type)
