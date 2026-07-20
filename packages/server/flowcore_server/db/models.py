import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base

class Pipeline(Base):
    __tablename__ = "pipelines"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    owner: Mapped[str] = mapped_column(String(255), default="unknown", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    tags: Mapped[list] = mapped_column(JSONB, default=[], nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    versions: Mapped[List["PipelineVersion"]] = relationship(
        "PipelineVersion", 
        back_populates="pipeline", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class PipelineVersion(Base):
    __tablename__ = "pipeline_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pipelines.id"), index=True, nullable=False)
    version_tag: Mapped[str] = mapped_column(String(100), nullable=False)
    
    dsl_definition: Mapped[dict] = mapped_column(JSONB, nullable=False)
    graph_definition: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Relationships
    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="versions")
    runs: Mapped[List["ExecutionRun"]] = relationship("ExecutionRun", back_populates="pipeline_version", lazy="selectin")

class ExecutionRun(Base):
    __tablename__ = "execution_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pipeline_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pipeline_versions.id"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    parameters: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    pipeline_version: Mapped["PipelineVersion"] = relationship("PipelineVersion", back_populates="runs")
    steps: Mapped[List["ExecutionStep"]] = relationship("ExecutionStep", back_populates="run", cascade="all, delete-orphan", lazy="selectin")

class ExecutionStep(Base):
    __tablename__ = "execution_steps"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("execution_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    step_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    logs: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    run: Mapped["ExecutionRun"] = relationship("ExecutionRun", back_populates="steps")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)
