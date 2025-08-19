import uuid

from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import UUID, Integer

from solkit.database.sql.orm.model import EntityModel


class EntityModelFactory:
    """Factory class for creating Entity models with different ID configurations."""
    
    @classmethod
    def integer_id(cls, auto_increment: bool = True) -> type[EntityModel]:
        """Create an entity model with integer ID."""
        class DynamicIntegerIdModel(EntityModel):
            __abstract__ = True
            
            id: Mapped[int] = mapped_column(
                Integer, 
                primary_key=True, 
                index=True, 
                nullable=False,
                unique=False,
                autoincrement=auto_increment
            )
        
        return DynamicIntegerIdModel
    
    @classmethod
    def uuid_id(cls, as_uuid: bool = True) -> type[EntityModel]:
        """Create an entity model with UUID ID."""

        class DynamicUUIDIdModel(EntityModel):
            __abstract__ = True
            
            id: Mapped[UUID] = mapped_column(
                UUID(as_uuid=as_uuid), 
                primary_key=True, 
                default=uuid.uuid4,
                index=True,
                nullable=False,
                unique=False
            )
        
        return DynamicUUIDIdModel
    
    # @classmethod
    # def string_id(cls, length: int | None = None) -> type[EntityModel]:
    #     """Create an entity model with string ID."""

    #     class DynamicStringIdModel(EntityModel):
    #         __abstract__ = True
     
    #         id: Mapped[str] = mapped_column(
    #             String(length=length), 
    #             primary_key=True, 
    #             index=True,
    #             nullable=False,
    #             unique=False
    #         )
        
    #     return DynamicStringIdModel
    
    @classmethod
    def multi_column_id(cls, columns: list[str]) -> type[EntityModel]:
        """Create an entity model with custom ID type."""

        class DynamicCustomIdModel(EntityModel):
            __abstract__ = True
            __table_args__ = (
                PrimaryKeyConstraint(
                    *columns,
                    name=f'pk_{"_".join(columns)}'
                )
            )
        
        return DynamicCustomIdModel
