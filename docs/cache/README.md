
# Python Cache - Redis Adapter

## Documentation

[Redis Documentation](https://redis.readthedocs.io/en/stable/index.html#)

[redis-py](https://redis.readthedocs.io/en/stable/connections.html#connecting-to-redis)

## Configuration

### Common Parameters

| Parameter              | Environment Variable         | Definition                                |
|------------------------|------------------------------|-------------------------------------------|
| deployment_mode        | CACHE_DEPLOYMENT_MODE        | cluster or single                         |

| Parameter              | Environment Variable         | Required | Definition                                |
|------------------------|------------------------------|----------|-------------------------------------------|
| username               | CACHE_USERNAME               |          |                                           |
| password               | CACHE_PASSWORD               |          |                                           |
| host                   | CACHE_HOST                   | *        | Redis cluster host address                |
| port                   | CACHE_PORT                   |          | Redis cluster port number                 |
| max_connections        | CACHE_MAX_CONNECTIONS        |          | Maximum number of connections in the pool |
| socket_timeout         | CACHE_SOCKET_TIMEOUT         |          | Socket timeout in seconds                 |
| socket_connect_timeout | CACHE_SOCKET_CONNECT_TIMEOUT |          | Socket connection timeout in seconds      |
| socket_keepalive       | CACHE_SOCKET_KEEPALIVE       |          | Enable socket keepalive                   |
| health_check_interval  | CACHE_HEALTH_CHECK_INTERVAL  |          | Health check interval in seconds          |
| retry_max_attempts     | CACHE_RETRY_MAX_ATTEMPTS     |          | Maximum number of retry attempts          |

### Cluster Specific Parameters

| Parameter                    | Environment Variable               | Definition                                |
|------------------------------|------------------------------------|-------------------------------------------|
| load_balancing_strategy      | CACHE_LOAD_BALANCING_STRATEGY      | round_robin or round_robin_replicas or random_replica |
| require_full_coverage        | CACHE_REQUIRE_FULL_COVERAGE        | Require full cluster coverage             |
| cluster_error_retry_attempts | CACHE_CLUSTER_ERROR_RETRY_ATTEMPTS | Number of times to retry on cluster error |

### Single Node Specific Parameters

| Parameter        | Environment Variable    | Definition                   |
|------------------|-------------------------|------------------------------|
| db               | CACHE_DB                | Redis database number (0-15) |
| retry_on_timeout | CACHE_RETRY_ON_TIMEOUT  | Retry commands on timeout    |

## Simple Usage

```python
# cache/__init__.py
from solkit.cache import RedisClusterAdapter

cache_redis_adapter = RedicsClusterAdapter.config()
# or
cache_redis_adapter = RedicsClusterAdapter.cluster_config()
# or
cache_redis_adapter = RedicsClusterAdapter.single_node_config()

async def get_cache_session():
    async with cache_redis_adapter.get_session() as cache_session:
        yield cache_session
```

```python
# app.py
from contextlib import asynccontextmanager

from fastapi import FastAPI

from cache import cache_redis_adapter


@asynccontextmanager
async def lifespan(app: FastAPI):
    await cache_redis_adapter.connect()
    yield
    await cache_redis_adapter.disconnect()


def application() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan
    )
    return app


app = application()
```

```python
# route.py
from typing import Any

from fastapi import APIRouter, Depends
from solkit.cache import CacheRepository

from cache import get_cache_session

router = APIRouter()

@router.get("/example")
async def example(cache_session = Depends(get_cache_session)) -> dict[str, Any]:
    service = ExampleService(CacheRepository(cache_session))
    return await service.process()

# or
from typing import Annotated
from redis.asyncio.client import Redis
from redis.asyncio.cluster import RedisCluster


@router.get("/example")
async def example(cache_session: Annotated[RedisCluster | Redis, Depends(get_cache_session)]) -> dict[str, Any]:
    service = ExampleService(CacheRepository(cache_session))
    return await service.process()
```

Expected logs for Single Node configuration

```bash
application        | INFO:     Started server process [1]
application        | INFO:     Waiting for application startup.
application        | INFO:solkit.cache.adapter:[ADAPTER][CACHE][CONNECTION URI: redis://redis-single-node:6379/1]
application        | INFO:solkit.cache.adapter:[ADAPTER][CACHE][CONNECTION MODE: SINGLE]
application        | INFO:solkit.cache.adapter:[ADAPTER][CACHE][CONNECTION ACTIVE: True]
application        | INFO:solkit.cache.adapter:[ADAPTER][CACHE][CONNECTION POOL ACTIVE: [<redis.asyncio.connection.Connection(host=redis-single-node,port=6379,db=1)>]]
application        | INFO:     Application startup complete.
application        | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Expectec logs for Cluster configuration

```bash
application        | INFO:     Started server process [1]
application        | INFO:     Waiting for application startup.
application        | INFO:solfacil.cache.adapter:[ADAPTER][CACHE][CONNECTION MODE: CLUSTER]
application        | INFO:solfacil.cache.adapter:[ADAPTER][CACHE][CONNECTION STATUS: True]
application        | INFO:     Application startup complete.
application        | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Application Graceful Shutdown logs:

```bash

```

## Repository Extension

```python
from typing import Any

from redis.asyncio.client import Redis
from redis.asyncio.cluster import RedisCluster
from solkit.cache import CacheRepository as CacheRepositoryMixin


class CacheRepository(CacheRepositoryMixin):
    __init__(self, cache_session: RedisCluster | Redis) -> None:
        super().__init__(cache_session)
    
    async def new_implementation(*args, **kwargs) -> Any:
        return self._cache_session.[method(*args, **kwargs)]
```

## Unit Test

```python
# conftest.py
from unittest.mock import AsyncMock, MagicMock

import pytest_asyncio
from solkit.cache import CacheRepository


@pytest_asyncio.fixture(scope="function")
async def cache_repository_mock() -> MagicMock:
    cache_repository_mock = MagicMock(spec=CacheRepository)
    cache_repository.set_key = AsyncMock()
    cache_repository.get_key = AsyncMock()
    # define all the methods that will be used
    ...

    return cache_repository_mock
```

```python
# test_example.py
import pytest

@pytest.mark.asyncio
async def test_example_service(cache_repository_mock):
    """A Dummy example of how to use CacheRepository Mock for unit tests"""
    # arrange
    cache_repository_mock.set_key.return_value = "something"
    service = ExampleService(cache_repository_mock)
    # act
    result = service.process()
    # assert
    cache_repository_mock.set_key.assert_called_once()
```
