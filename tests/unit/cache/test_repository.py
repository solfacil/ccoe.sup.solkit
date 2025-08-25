from unittest.mock import AsyncMock, Mock

import pytest
from redis.asyncio.client import Redis
from redis.asyncio.cluster import RedisCluster

from solkit.cache.repository import CacheRepository

CacheAdapter = Redis | RedisCluster

pytestmark = pytest.mark.parametrize(
    'cache_adapter',
    [
        pytest.param(Redis, id='single'),
        pytest.param(RedisCluster, id='cluster'),
    ],
)


def test_cache_repository_static_encode_then_return_bytes(cache_adapter: CacheAdapter) -> None:
    """Test the encode value method."""
    # arrange
    cache_adapter_mock = Mock(spec=cache_adapter)
    cache_repository = CacheRepository(cache_session=cache_adapter_mock)
    # act
    encoded_value = cache_repository._encode('value')
    # assert
    assert encoded_value == b'value'
    cache_adapter_mock.assert_not_called()


def test_cache_repository_static_encode_hash_mapping_then_return_string(cache_adapter: CacheAdapter) -> None:
    """Test the encode value method."""
    # arrange
    cache_adapter_mock = Mock(spec=cache_adapter)
    cache_repository = CacheRepository(cache_session=cache_adapter_mock)
    # act
    encoded_value = cache_repository._encode_hash_mapping({'key': 'value'})
    # assert
    assert encoded_value == '{"key": "value"}'
    cache_adapter_mock.assert_not_called()


def test_cache_repository_static_decode_bytes_then_return_string(cache_adapter: CacheAdapter) -> None:
    """Test the decode value method."""
    # arrange
    cache_adapter_mock = Mock(spec=cache_adapter)
    cache_repository = CacheRepository(cache_session=cache_adapter_mock)
    # act
    decoded_value = cache_repository._decode(b'value')
    # assert
    assert decoded_value == 'value'
    cache_adapter_mock.assert_not_called()


@pytest.mark.asyncio
async def test_cache_repository_set_key_without_ttl(cache_adapter: CacheAdapter) -> None:
    """Test the set key method."""
    # arrange
    cache_adapter_mock = AsyncMock(spec=cache_adapter)
    cache_adapter_mock.set = AsyncMock(return_value=True)
    cache_adapter_mock.expire = AsyncMock(return_value=True)
    cache_repository = CacheRepository(cache_session=cache_adapter_mock)
    key = 'key'
    value = 'value'
    # act
    result = await cache_repository.set_key(key, value)
    # assert
    assert result is True
    cache_adapter_mock.set.assert_awaited_once()
    cache_adapter_mock.expire.assert_not_called()


@pytest.mark.asyncio
async def test_cache_repository_set_key_with_ttl(cache_adapter: CacheAdapter) -> None:
    """Test the set key method with ttl."""
    # arrange
    cache_adapter_mock = AsyncMock(spec=cache_adapter)
    cache_adapter_mock.set = AsyncMock(return_value=True)
    cache_adapter_mock.expire = AsyncMock(return_value=True)
    cache_repository = CacheRepository(cache_session=cache_adapter_mock)
    key = 'key'
    value = 'value'
    ttl = 10
    # act
    result = await cache_repository.set_key(key, value, ttl)
    # assert
    assert result is True
    cache_adapter_mock.set.assert_awaited_once()
    cache_adapter_mock.expire.assert_called_once_with(key, ttl)


@pytest.mark.asyncio
async def test_cache_repository_get_key(cache_adapter: CacheAdapter) -> None:
    """Test the get key method."""
    # arrange
    cache_adapter_mock = AsyncMock(spec=cache_adapter)
    cache_adapter_mock.get = AsyncMock(return_value=b'value')
    cache_repository = CacheRepository(cache_session=cache_adapter_mock)
    key = 'key'
    # act
    result = await cache_repository.get_key(key)
    # assert
    assert result == 'value'
    cache_adapter_mock.get.assert_awaited_once_with(key)


@pytest.mark.asyncio
async def test_cache_repository_exists_key(cache_adapter: CacheAdapter) -> None:
    """Test the exists key method."""
    # arrange
    cache_adapter_mock = AsyncMock(spec=cache_adapter)
    cache_adapter_mock.exists = AsyncMock(return_value=1)
    cache_repository = CacheRepository(cache_session=cache_adapter_mock)
    key = 'key'
    # act
    result = await cache_repository.exists_key(key)
    # assert
    assert result is True
    cache_adapter_mock.exists.assert_awaited_once_with(key)


@pytest.mark.asyncio
async def test_cache_repository_delete_key(cache_adapter: CacheAdapter) -> None:
    """Test the delete key method."""
    # arrange
    cache_adapter_mock = AsyncMock(spec=cache_adapter)
    cache_adapter_mock.delete = AsyncMock(return_value=1)
    cache_repository = CacheRepository(cache_session=cache_adapter_mock)
    key = 'key'
    # act
    result = await cache_repository.delete_key(key)
    # assert
    assert result is True
    cache_adapter_mock.delete.assert_awaited_once_with(key)


@pytest.mark.asyncio
async def test_cache_repository_set_hash(cache_adapter: CacheAdapter) -> None:
    """Test the set hash method."""
    # arrange
    name = 'name'
    mapping = {'key': 'value'}
    ttl = 10
    cache_adapter_mock = AsyncMock(spec=cache_adapter)
    cache_adapter_mock.hset = AsyncMock(return_value=1)
    cache_adapter_mock.expire = AsyncMock(return_value=True)
    cache_repository = CacheRepository(cache_session=cache_adapter_mock)
    # act
    result = await cache_repository.set_hash(name, mapping, ttl)
    # assert
    assert result is True
    cache_adapter_mock.hset.assert_awaited_once()


@pytest.mark.asyncio
async def test_cache_repository_get_hash(cache_adapter: CacheAdapter) -> None:
    """Test the get hash method."""
    # arrange
    name = 'name'
    field = 'key'
    value = 'value'
    cache_adapter_mock = AsyncMock(spec=cache_adapter)
    cache_adapter_mock.hget = AsyncMock(return_value=value.encode('utf-8'))
    cache_repository = CacheRepository(cache_session=cache_adapter_mock)

    # act
    result = await cache_repository.get_hash(name, field)
    # assert
    assert result == value
    cache_adapter_mock.hget.assert_awaited_once_with(name, field)


@pytest.mark.asyncio
async def test_cache_repository_exists_hash(cache_adapter: CacheAdapter) -> None:
    """Test the exists hash method."""
    # arrange
    cache_adapter_mock = AsyncMock(spec=cache_adapter)
    cache_adapter_mock.hexists = AsyncMock(return_value=True)
    cache_repository = CacheRepository(cache_session=cache_adapter_mock)
    name = 'name'
    field = 'key'
    # act
    result = await cache_repository.exists_hash(name, field)
    # assert
    assert result is True
    cache_adapter_mock.hexists.assert_awaited_once_with(name, field)


@pytest.mark.asyncio
async def test_cache_repository_delete_hash(cache_adapter: CacheAdapter) -> None:
    """Test the delete hash method."""
    # arrange
    cache_adapter_mock = AsyncMock(spec=cache_adapter)
    cache_adapter_mock.hdel = AsyncMock(return_value=1)
    cache_repository = CacheRepository(cache_session=cache_adapter_mock)
    name = 'name'
    field = 'key'
    # act
    result = await cache_repository.delete_hash(name, field)
    # assert
    assert result is True
    cache_adapter_mock.hdel.assert_awaited_once_with(name, field)


@pytest.mark.asyncio
async def test_cache_repository_healthcheck_then_return_healthy(cache_adapter: CacheAdapter) -> None:
    """Test the healthcheck method."""
    # arrange
    cache_adapter_mock = AsyncMock(spec=cache_adapter)
    cache_adapter_mock.ping = AsyncMock(return_value=b'PONG')
    cache_repository = CacheRepository(cache_session=cache_adapter_mock)
    # act
    result = await cache_repository.healthcheck()
    # assert
    assert result[0] is True
    assert result[1] is None
    cache_adapter_mock.ping.assert_awaited_once()


@pytest.mark.asyncio
async def test_cache_repository_healthcheck_then_return_unhealthy(cache_adapter: CacheAdapter) -> None:
    """Test the healthcheck method."""
    # arrange
    cache_adapter_mock = AsyncMock(spec=cache_adapter)
    cache_adapter_mock.ping = AsyncMock(side_effect=Exception('Connection error'))
    cache_repository = CacheRepository(cache_session=cache_adapter_mock)
    # act
    result = await cache_repository.healthcheck()
    # assert
    assert result[0] is False
    assert result[1] == 'Connection error'
    cache_adapter_mock.ping.assert_awaited_once()
