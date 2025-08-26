from collections.abc import Sequence
from typing import Any

from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import asc, delete, desc, insert, text, update
from sqlalchemy.sql.selectable import Select

from .constants import (
    DATABASE_DEFAULT_OFFSET,
    DATABASE_DEFAULT_PAGE_SIZE,
    DATABASE_DEFAULT_SORT_COLUMN,
    DATABASE_DEFAULT_SORT_TYPE,
    DATABASE_HEALTHCHECK_QUERY,
    DatabaseSQLSort,
)
from .orm import EntityModel


class DatabaseSQLRepository:
    """Repository for the database."""

    def __init__(self, database_session: AsyncSession, model: type[EntityModel] | None) -> None:
        """Initialize the database repository."""
        self._database_session = database_session
        self._model = model

    async def commit(self) -> None:
        """Commit the database session."""
        await self._database_session.commit()

    async def get_by_id(self, model_id: int | str) -> Row[tuple[EntityModel]] | None:
        """Get a model by id."""
        if self._model is None:
            raise ValueError('Model is not set')

        stmt = select(self._model).where(self._model.id == model_id)
        result = await self._database_session.execute(stmt)
        result = result.one_or_none()
        return result

    async def insert(self, data: dict[str, Any]) -> Row[tuple[EntityModel]] | None:
        """Insert a model."""
        if self._model is None:
            raise ValueError('Model is not set')

        stmt = insert(self._model).values(data).returning(self._model)
        result = await self._database_session.execute(stmt)
        result = result.one_or_none()
        return result

    async def update(self, model_id: int | str, data: dict[str, Any]) -> Row[tuple[EntityModel]] | None:
        """Update a model by id."""
        if self._model is None:
            raise ValueError('Model is not set')

        stmt = update(self._model).where(self._model.id == model_id).values(data).returning(self._model)
        result = await self._database_session.execute(stmt)
        result = result.one_or_none()
        return result

    async def delete(self, model_id: int | str) -> Row[tuple[EntityModel]] | None:
        """Delete a model."""
        if self._model is None:
            raise ValueError('Model is not set')

        stmt = delete(self._model).where(self._model.id == model_id).returning(self._model)
        result = await self._database_session.execute(stmt)
        result = result.one_or_none()
        return result

    async def _set_order_by(self, stmt: Select, sort: DatabaseSQLSort) -> Select:
        if self._model is None:
            raise ValueError('Model is not set')

        columns_and_orders = {
            column_orders.split(':')[0]: column_orders.split(':')[1]
            for column_orders in sort.split(',')
            if len(column_orders.split(':')) > 1
        } or {DATABASE_DEFAULT_SORT_COLUMN: DATABASE_DEFAULT_SORT_TYPE}

        for column, order in columns_and_orders.items():
            if column in self._model.__table__.columns:
                if order == str(DatabaseSQLSort.DESC):
                    stmt = stmt.order_by(desc(column))
                elif order == str(DatabaseSQLSort.ASC):
                    stmt = stmt.order_by(asc(column))

        return stmt

    async def _get_page(self, stmt: Select, limit: int, offset: int) -> Sequence[Row[tuple[EntityModel]]]:
        stmt = stmt.offset(offset).limit(limit)
        result = await self._database_session.execute(statement=stmt)
        result = result.scalars().all()
        return result

    async def paginate(
        self,
        limit: int = DATABASE_DEFAULT_PAGE_SIZE,
        offset: int = DATABASE_DEFAULT_OFFSET,
        sort: DatabaseSQLSort | None = None,
    ) -> Sequence[Row[tuple[EntityModel]]]:
        """Paginate the models."""
        if self._model is None:
            raise ValueError('Model is not set')
        stmt = select(self._model)
        if sort:
            stmt = await self._set_order_by(stmt=stmt, sort=sort)
        result = await self._get_page(stmt=stmt, limit=limit, offset=offset)
        return result

    async def healthcheck(self) -> tuple[bool, str | None]:
        """Healthcheck the database."""
        try:
            await self._database_session.execute(text(DATABASE_HEALTHCHECK_QUERY))
            return True, None
        except Exception as err:
            return False, str(err)
