from typing import Any, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from .orm.model import EntityModel


class DatabaseSQLRepositoryProtocol(Protocol):
    """Protocol for the database repository."""
    
    def __init__(self, database_session: AsyncSession, model: type[EntityModel]) -> None:
        """Initialize the database repository."""
        ...
    
    async def commit(self) -> None:
        """Commit the database session."""
        ...
    
    async def get_by_id(self, id: int) -> type[EntityModel] | None:
        """Get a model by id."""
        ...
    
    async def insert(self, data: dict[str, Any]) -> type[EntityModel]:
        """Insert a model."""
        ...
    
    async def update(self, data: dict[str, Any]) -> type[EntityModel] | None:
        """Update a model."""
        ...
    
    async def delete(self, data: type[EntityModel]) -> type[EntityModel] | None:
        """Delete a model."""
        ...
