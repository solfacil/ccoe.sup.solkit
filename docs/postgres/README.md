
# Python PostgreSQL - SQL Alchemy Adapter

## Documentations

[PostgreSQL](https://www.postgresql.org/docs/)

[SQLAlchemy](https://docs.sqlalchemy.org/en/20/)

## Usage

```python
from solkit.database.sql.postgres import DatabasePostgreSQLAdapter

database_postgresql_adapter = DatabasePostgreSQLAdapter.config()

async def get_database_session():
    async with database_postgresql_adapter.get_session() as database_session:
        yield database_session

async def get_database_connection():
    async with database_postgresql_adapter.get_connection() as database_connection:
        yield database_connection
```

```python
# database/models/example.py
from solkit.postgres import EntityModel


class ExampleModel(EntityModel)
    __tablename__ = "example"
    __table_args__ = {

    }

    ### columns definitions ###
```

```python
# route.py
from fastapi import APIRouter, Depends
from solkit.database.sql.postgres import DatabasePostgreSQLRepository

from database import get_database_session
from datamase.models import ExampleModel

router = APIRouter()


@router.get(path="/example")
async def example(database_session = Depends(get_database_session)):
    service = ExampleService(DatabasePostgreSQLRepository(database_session, ExampleModel))
    return await service.process()
```

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import database_postgresql_adapter
from route import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database_postgresql_adapter.connect()
    yield
    await database_postgresql_adapter.disconnect()
    
def application() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
    )
    app.include_router(router)
    return app


app = application()
```

Expected logs for Single RW instances:

```bash
application           | INFO:     Started server process [1]
application           | INFO:     Waiting for application startup.
application           | INFO:solkit.database.sql.postgres.adapter:[ADAPTER][DATABASE][ENGINE][URI: postgresql+asyncpg://postgres:***@postgres-single-node:5432/postgres]
application           | INFO:solkit.database.sql.postgres.adapter:[ADAPTER][DATABASE][CONNECTION RW ACTIVE: 1]
application           | INFO:     Application startup complete.
application           | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Expected logs for Cluster with RW and RO instances:

```bash
application           | INFO:     Started server process [1]
application           | INFO:     Waiting for application startup.
application           | INFO:solkit.database.sql.postgres.adapter:[ADAPTER][DATABASE][ENGINE][URI: postgresql+asyncpg://postgres:***@postgres-single-node:5432/postgres]
application           | INFO:solkit.database.sql.postgres.adapter:[ADAPTER][DATABASE][CONNECTION RW ACTIVE: 1]
application           | INFO:solkit.database.sql.postgres.adapter:[ADAPTER][DATABASE][ENGINE][URI: postgresql+asyncpg://postgres:***@postgres-single-node:5432/postgres]
application           | INFO:solkit.database.sql.postgres.adapter:[ADAPTER][DATABASE][CONNECTION RO ACTIVE: 1]
application           | INFO:     Application startup complete.
application           | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Configuration

The configuration is handled through environment variables using Pydantic settings.
Here are the available configuration options:

| Parameter            | Type | Environment Variable          | Description |
|----------------------|------|-------------------------------|-------------|
| driver               | str  | DATABASE_DRIVER               | Database driver |
| dialect              | str  | DATABASE_DIALECT              | Database dialect |
| username             | str  | DATABASE_USERNAME             | Database username |
| password             | str  | DATABASE_PASSWORD             | Database password |
| host_rw              | str  | DATABASE_HOST_RW              | Database host read/write |
| host_ro              | str  | DATABASE_HOST_RO              | Database host read only |
| port                 | int  | DATABASE_PORT                 | Database port |
| database             | str  | DATABASE_NAME                 | Database name |
| pool_size            | int  | DATABASE_POOL_SIZE            | Database pool size |
| max_overflow         | int  | DATABASE_MAX_OVERFLOW         | Database max overflow |
| pool_recycle_seconds | int  | DATABASE_POOL_RECYCLE_SECONDS | Database pool recycle seconds |
| pool_timeout_seconds | int  | DATABASE_POOL_TIMEOUT_SECONDS | Database pool timeout seconds |
| pool_pre_ping        | bool | DATABASE_POOL_PRE_PING        | Database pool pre ping |
| echo_sql             | str  | DATABASE_ECHO_SQL             | Database echo SQL |
