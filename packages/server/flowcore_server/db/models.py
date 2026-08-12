import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base

class Folder(Base):
    __tablename__ = "folders"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=True)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("folders.id", ondelete="CASCADE"), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Relationships
    subfolders: Mapped[List["Folder"]] = relationship("Folder", backref="parent", remote_side=[id])
    pipelines: Mapped[List["Pipeline"]] = relationship("Pipeline", back_populates="folder")

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

class PipelineTag(Base):
    __tablename__ = "pipeline_tags"
    
    pipeline_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pipelines.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

class UserPipelineFavorite(Base):
    __tablename__ = "user_pipeline_favorites"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pipelines.id", ondelete="CASCADE"), primary_key=True)

class UserRecentPipeline(Base):
    __tablename__ = "user_recent_pipelines"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pipelines.id", ondelete="CASCADE"), primary_key=True)
    last_accessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

class UserWorkspaceSettings(Base):
    __tablename__ = "user_workspace_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    preferred_view: Mapped[str] = mapped_column(String(50), default="grid", nullable=False)
    default_sort: Mapped[str] = mapped_column(String(50), default="updated_at", nullable=False)
    sidebar_collapsed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expanded_folders: Mapped[list] = mapped_column(JSONB, default=[], nullable=False)


class Pipeline(Base):
    __tablename__ = "pipelines"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=True)
    folder_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("folders.id", ondelete="SET NULL"), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    owner: Mapped[str] = mapped_column(String(255), default="unknown", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    tags: Mapped[list] = mapped_column(JSONB, default=[], nullable=False) # Legacy text tags
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    versions: Mapped[List["PipelineVersion"]] = relationship(
        "PipelineVersion", 
        back_populates="pipeline", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    folder: Mapped[Optional["Folder"]] = relationship("Folder", back_populates="pipelines")

class PipelineVersion(Base):
    __tablename__ = "pipeline_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=True)
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
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=True)
    pipeline_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pipeline_versions.id"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    parameters: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    outputs: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)

    # Relationships
    pipeline_version: Mapped["PipelineVersion"] = relationship("PipelineVersion", back_populates="runs")
    steps: Mapped[List["ExecutionStep"]] = relationship("ExecutionStep", back_populates="run", cascade="all, delete-orphan", lazy="selectin")

class ExecutionStep(Base):
    __tablename__ = "execution_steps"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=True)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("execution_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    step_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    outputs: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)
    logs: Mapped[list] = mapped_column(JSONB, default=[], nullable=False)

    # Relationships
    run: Mapped["ExecutionRun"] = relationship("ExecutionRun", back_populates="steps")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)

class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pipelines.id", ondelete="CASCADE"), index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    expression: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)
    
    max_retries: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    retry_delay_seconds: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    holiday_calendar: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    blackout_windows: Mapped[list] = mapped_column(JSONB, default=[], nullable=False)
    
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    pipeline: Mapped["Pipeline"] = relationship("Pipeline")

class ScheduleRunHistory(Base):
    __tablename__ = "schedule_run_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=True)
    schedule_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("schedules.id", ondelete="CASCADE"), index=True, nullable=False)
    execution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("execution_runs.id", ondelete="CASCADE"), nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships
    schedule: Mapped["Schedule"] = relationship("Schedule")
    execution: Mapped["ExecutionRun"] = relationship("ExecutionRun")

from .auth_models import Organization, Workspace, User, Role, Permission, RolePermission, WorkspaceMember
from .environment_models import Environment, EnvironmentVariable, PipelineEnvironmentBinding
from .lineage_models import Dataset, DatasetVersion, DatasetColumn, LineageEdge, ExecutionLineage, DatasetTag, DatasetMetadata
