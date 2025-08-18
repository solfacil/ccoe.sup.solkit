from typing import Any

from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import asc, desc, delete, insert, update
from sqlalchemy.sql.schema import Sequence
from sqlalchemy.sql.selectable import Select

from .constants import (
    DATABASE_DEFAULT_OFFSET, 
    DATABASE_DEFAULT_PAGE_SIZE, 
    DATABASE_DEFAULT_SORT_COLUMN, 
    DATABASE_DEFAULT_SORT_TYPE, 
    DatabasePostgresSortType,
)
from .model import EntityModel


class DatabasePostgreSQLRepository:
    """Repository for the database."""
    
    def __init__(self, database_session: AsyncSession, model: type[EntityModel]) -> None:
        """Initialize the database repository."""
        self._database_session = database_session
        self._model = model

    async def commit(self) -> None:
        """Commit the database session."""
        await self._database_session.commit()
    
    async def get_by_id(self, model_id: int | str) -> Row[tuple[EntityModel]] | None:
        """Get a model by id."""
        stmt = select(self._model).where(self._model.id == model_id)
        result = await self._database_session.execute(stmt)
        result = result.one_or_none()
        return result
    
    async def insert(self, data: dict[str, Any]) -> Row[tuple[EntityModel]] | None:
        """Insert a model."""
        stmt = insert(self._model).values(data).returning(self._model)
        result = await self._database_session.execute(stmt)
        result = result.one_or_none()
        return result
        
    async def update(self, model_id: int | str, data: dict[str, Any]) -> Row[tuple[EntityModel]] | None:
        """Update a model by id."""
        stmt = update(self._model).where(self._model.id == model_id).values(data).returning(self._model)
        result = await self._database_session.execute(stmt)
        result = result.one_or_none()
        return result
    
    async def delete(self, model_id: int | str) -> Row[tuple[EntityModel]] | None:
        """Delete a model."""
        stmt = delete(self._model).where(self._model.id == model_id).returning(self._model)
        result = await self._database_session.execute(stmt)
        result = result.one_or_none()
        return result
    
    async def _set_order_by(self, stmt: Select, sort: DatabasePostgresSortType) -> Select:
        columns_and_orders = {
            column_orders.split(':')[0]: column_orders.split(':')[1]
            for column_orders in sort.split(',')
            if len(column_orders.split(':')) > 1
        } or {DATABASE_DEFAULT_SORT_COLUMN: DATABASE_DEFAULT_SORT_TYPE}

        for column, order in columns_and_orders.items():
            if column in  self._model.__table__.columns:
                if order == str(DatabasePostgresSortType.DESC):
                    stmt = stmt.order_by(desc(column))
                elif order == str(DatabasePostgresSortType.ASC):
                    stmt = stmt.order_by(asc(column))

        return stmt
    
    async def _get_page(self, stmt: Select, limit: int, offset: int):
        stmt = stmt.offset(offset).limit(limit)
        result = await self._database_session.execute(statement=stmt)
        result = result.scalars().all()
        return result
    
    async def paginate(
        self,
        limit: int = DATABASE_DEFAULT_PAGE_SIZE,
        offset: int = DATABASE_DEFAULT_OFFSET,
        sort: DatabasePostgresSortType | None = None,
    ):
        """Paginate the models."""
        stmt = select(self._model)
        if sort:
            stmt = await self._set_order_by(stmt=stmt, sort=sort)
        result = await self._get_page(stmt=stmt, limit=limit, offset=offset)
        return result
    
    async def healthcheck(self) -> tuple[bool, str | None]:
        """Healthcheck the database."""
        stmt = select(1)
        try:
            await self._database_session.execute(stmt)
            return True, None
        except Exception as err:
            return False, str(err)
