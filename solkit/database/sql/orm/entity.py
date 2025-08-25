from datetime import datetime
from typing import Any

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime

from .base import BaseModel


class EntityModel(BaseModel):
    """Entity base model."""

    __abstract__ = True

    id: Mapped[Any]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
