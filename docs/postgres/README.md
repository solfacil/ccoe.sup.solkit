
# Python PostgreSQL - SQL Alchemy Adapter

## Documentations

[PostgreSQL](https://www.postgresql.org/docs/)

[SQLAlchemy](https://docs.sqlalchemy.org/en/20/)

## Usage

```python
# postgres/__init__.py
from solkit.postgres import DatabasePostgreSQLAdapter

database_postgresql_adapter = DatabasePostgreSQLAdapter.config("")
```

```python

```

```python

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
