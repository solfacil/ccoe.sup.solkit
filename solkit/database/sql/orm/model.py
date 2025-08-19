from datetime import datetime
from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import DateTime, Integer

from ..constants import DATABASE_INDEXES_NAMING_CONVENTION

metadata = MetaData(naming_convention=DATABASE_INDEXES_NAMING_CONVENTION)


class BaseModel(DeclarativeBase):
    """Base model for the database."""
    
    metadata = metadata
    
    def __repr__(self) -> str:
        """Return the string representation of the model."""
        columns = ', '.join([
            f'{k}={repr(v)}' 
            for k, v in self.__dict__.items() 
            if not k.startswith('_')
        ])
        return f'<{self.__class__.__name__}({columns})>'
    
    def to_dict(self) -> dict[str, Any]:
        """Return the dictionary representation of the model."""
        return {
            k: v 
            for k, v in self.__dict__.items() 
            if not k.startswith('_')
        }


class EntityModel(BaseModel):
    """Entity base model."""
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), onupdate=datetime.now())


# class EntityModelIntegerId(EntityModel):
#    """Entity base model with integer id."""
#    
#    id: Mapped[int] = mapped_column(Integer, primary_key=True)


# class EntityModelStringId(EntityModel):
#    """Entity base model with string id."""
#    
#    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4())
