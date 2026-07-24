import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base

class EnvironmentVariable(Base):
    __tablename__ = "environment_variables"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    environment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("environments.id", ondelete="CASCADE"), index=True, nullable=False)
    key: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    value: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Used if not secret
    is_secret: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    encrypted_value: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Used if secret
    
    environment: Mapped["Environment"] = relationship("Environment", back_populates="variables")

class PipelineEnvironmentBinding(Base):
    __tablename__ = "pipeline_environment_bindings"
    
    pipeline_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pipelines.id", ondelete="CASCADE"), primary_key=True)
    environment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("environments.id", ondelete="CASCADE"), primary_key=True)

class Environment(Base):
    __tablename__ = "environments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    variables: Mapped[List["EnvironmentVariable"]] = relationship(
        "EnvironmentVariable",
        back_populates="environment",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    workspace: Mapped["Workspace"] = relationship("Workspace")
