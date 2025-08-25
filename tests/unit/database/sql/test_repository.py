from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from solkit.database.sql.orm import EntityModel
from solkit.database.sql.repository import DatabaseSQLRepository


@pytest.mark.asyncio
async def test_database_sql_repository_commit() -> None:
    """Test the commit method."""
    # arrange
    database_adapter_mock = AsyncMock(spec=AsyncSession)
    database_repository = DatabaseSQLRepository(database_adapter_mock, None)
    # act
    await database_repository.commit()
    # assert
    database_adapter_mock.commit.assert_awaited_once()


# @pytest.mark.asyncio
# async def test_database_sql_repository_get_by_id_then_return_model() -> None:
#     """Test the get_by_id method."""
#     # arrange
#     entity_model_id = 1
#     database_adapter_mock = AsyncMock(spec=AsyncSession)
#     database_repository = DatabaseSQLRepository(database_adapter_mock, EntityModel)
#     # act
#     result = await database_repository.get_by_id(entity_model_id)
#     # assert
#     assert result is not None
#     assert result.id == entity_model_id
#     database_adapter_mock.execute.assert_awaited_once()


# @pytest.mark.asyncio
# async def test_database_sql_repository_get_by_id_then_return_none() -> None:
#     """Test the get_by_id method."""
#     # arrange
#     entity_model_id = 1
#     database_adapter_mock = AsyncMock(spec=AsyncSession)
#     database_repository = DatabaseSQLRepository(database_adapter_mock, EntityModel)
#     # act
#     result = await database_repository.get_by_id(entity_model_id)
#     # assert
#     assert result is None
#     database_adapter_mock.execute.assert_awaited_once()


# @pytest.mark.asyncio
# async def test_database_sql_repository_insert_then_return_model() -> None:
#     """Test the insert method."""
#     # arrange
#     database_adapter_mock = AsyncMock(spec=AsyncSession)
#     database_repository = DatabaseSQLRepository(database_adapter_mock, EntityModel)
#     # act
#     await database_repository.insert({"some": "data"})
#     # assert
#     database_adapter_mock.execute.assert_awaited_once()


# @pytest.mark.asyncio
# async def test_database_sql_repository_update_then_return_model() -> None:
#     """Test the update method."""
#     # arrange
#     entity_model_id = 1
#     database_adapter_mock = AsyncMock(spec=AsyncSession)
#     database_repository = DatabaseSQLRepository(database_adapter_mock, EntityModel)
#     # act
#     await database_repository.update(entity_model_id, {"another": "data"})
#     # assert
#     database_adapter_mock.execute.assert_awaited_once()


# @pytest.mark.asyncio
# async def test_database_sql_repository_delete_then_return_model() -> None:
#     """Test the delete method."""
#     # arrange
#     entity_model_id = 1
#     database_adapter_mock = AsyncMock(spec=AsyncSession)
#     database_repository = DatabaseSQLRepository(database_adapter_mock, EntityModel)
#     # act
#     result = await database_repository.delete(entity_model_id)
#     # assert
#     database_adapter_mock.execute.assert_awaited_once()
#     assert result is not None
#     assert result.id == entity_model_id
