import uuid
from datetime import datetime, timezone
from sqlalchemy import MetaData, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Naming conventions to ensure predictable constraint names (important for Alembic auto-generation)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata_obj = MetaData(naming_convention=convention)

def utc_now():
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    metadata = metadata_obj
    
    # Common columns for all tables
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
