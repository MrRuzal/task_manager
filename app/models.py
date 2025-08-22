from sqlalchemy import Column, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid
from enum import IntEnum


class Status(IntEnum):
    created = 1
    in_progress = 2
    completed = 3


class Task(Base):
    __tablename__ = "tasks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(
        Enum(Status, native_enum=False), default=Status.created, nullable=False
    )
