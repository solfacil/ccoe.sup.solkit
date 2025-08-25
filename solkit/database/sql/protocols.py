from typing import Any, Protocol, Sequence

from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession

from .constants import DATABASE_DEFAULT_PAGE_SIZE, DATABASE_DEFAULT_OFFSET, DatabaseSQLSort
from .orm import EntityModel


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

    async def paginate(
        self,
        limit: int = DATABASE_DEFAULT_PAGE_SIZE,
        offset: int = DATABASE_DEFAULT_OFFSET,
        sort: DatabaseSQLSort | None = None,
    ) -> Sequence[Row[tuple[EntityModel]]]:
        """Paginate the database session."""
        ...
