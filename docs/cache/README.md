
# Python Cache - Redis Adapter

## Documentation

[Redis Documentation](https://redis.readthedocs.io/en/stable/index.html#)

[redis-py](https://redis.readthedocs.io/en/stable/connections.html#connecting-to-redis)

## Usage

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
from fastapi import APIRouter, Depends
from solkit.cache import CacheRepository

from cache import get_cache_session

router = APIRouter()

@router.get("/example")
async def example(cache_session = Depends(get_cache_session)):
    service = ExampleService(CacheRepository(cache_session))
    return await service.process()
```

Expected logs for Single Node configuration

```bash
application        | INFO:     Started server process [1]
application        | INFO:     Waiting for application startup.
application        | INFO:solkit.cache.adapter:[ADAPTER][CACHE][CONNECTION URI: redis://redis-single-node:6379/1]
application        | INFO:solkit.cache.adapter:[ADAPTER][CACHE][CONNECTION MODE: SINGLE_NODE]
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

## Configuration

### Common Parameters

| Parameter              | Environment Variable         | Definition                                |
|------------------------|------------------------------|-------------------------------------------|
| deployment_mode        | CACHE_DEPLOYMENT_MODE        | cluster or single_node                    |

| Parameter              | Environment Variable         | Definition                                |
|------------------------|------------------------------|-------------------------------------------|
| host                   | CACHE_HOST                   | Redis cluster host address                |
| port                   | CACHE_PORT                   | Redis cluster port number                 |
| max_connections        | CACHE_MAX_CONNECTIONS        | Maximum number of connections in the pool |
| socket_timeout         | CACHE_SOCKET_TIMEOUT         | Socket timeout in seconds                 |
| socket_connect_timeout | CACHE_SOCKET_CONNECT_TIMEOUT | Socket connection timeout in seconds      |
| socket_keepalive       | CACHE_SOCKET_KEEPALIVE       | Enable socket keepalive                   |
| health_check_interval  | CACHE_HEALTH_CHECK_INTERVAL  | Health check interval in seconds          |
| retry_max_attempts     | CACHE_RETRY_MAX_ATTEMPTS     | Maximum number of retry attempts          |

### Cluster Specific Parameters

| Parameter                    | Environment Variable               | Definition                                |
|------------------------------|------------------------------------|-------------------------------------------|
| db                           | CACHE_DB                           | 0 or NULL/None                            |
| read_from_replicas           | CACHE_READ_FROM_REPLICAS           | Allow reading from replica nodes          |
| require_full_coverage        | CACHE_REQUIRE_FULL_COVERAGE        | Require full cluster coverage             |
| cluster_error_retry_attempts | CACHE_CLUSTER_ERROR_RETRY_ATTEMPTS | Number of times to retry on cluster error |

### Single Node Specific Parameters

| Parameter        | Environment Variable    | Definition                   |
|------------------|-------------------------|------------------------------|
| db               | CACHE_DB                | Redis database number (0-15) |
| retry_on_timeout | CACHE_RETRY_ON_TIMEOUT  | Retry commands on timeout    |
