"""
SQLAlchemy ORM models for the PMO application.
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class WorkflowStatus(str, PyEnum):
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_REVIEW = "awaiting_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


class ApprovalStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# ── Workflow Instance ─────────────────────────────────────────────────
class WorkflowInstance(Base):
    __tablename__ = "workflow_instances"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    thread_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    workflow_type: Mapped[str] = mapped_column(String, index=True)
    project_id: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[WorkflowStatus] = mapped_column(
        Enum(WorkflowStatus), default=WorkflowStatus.PENDING
    )
    input_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    user_id: Mapped[str] = mapped_column(String)
    user_role: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    correlation_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)

    approvals: Mapped[list["ApprovalRecord"]] = relationship(back_populates="workflow")
    audit_events: Mapped[list["AuditEvent"]] = relationship(back_populates="workflow")


# ── Approval Record ───────────────────────────────────────────────────
class ApprovalRecord(Base):
    __tablename__ = "approval_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflow_instances.id"))
    checkpoint_name: Mapped[str] = mapped_column(String)
    reviewer_id: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus), default=ApprovalStatus.PENDING
    )
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)

    workflow: Mapped["WorkflowInstance"] = relationship(back_populates="approvals")


# ── Audit Event ───────────────────────────────────────────────────────
class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id: Mapped[str | None] = mapped_column(
        ForeignKey("workflow_instances.id"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(String, index=True)
    actor_id: Mapped[str] = mapped_column(String)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    correlation_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)

    workflow: Mapped["WorkflowInstance | None"] = relationship(back_populates="audit_events")
