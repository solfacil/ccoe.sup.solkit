from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

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
            column.key: getattr(self, column.key) 
            for column in self.__mapper__.columns
        }
    
    # def set_table_args(self, values: dict[str, Any]) -> None:
    #     """Update the table arguments for the model."""
    #     self.__table_args__.update(values)
