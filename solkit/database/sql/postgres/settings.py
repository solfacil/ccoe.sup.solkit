from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL

from .constants import DatabasePostgresEcho


class DatabasePostgreSQLSettings(BaseSettings):
    """Database PostgreSQL settings."""
        
    driver: str = Field(
        default="asyncpg",
        description="Database driver",
        validation_alias="DATABASE_DRIVER"
    )
    dialect: str = Field(
        default="postgresql",
        description="Database dialect",
        validation_alias="DATABASE_DIALECT"
    )
    username: str = Field(
        default=...,
        description="Database username",
        validation_alias="DATABASE_USERNAME"
    )
    password: str = Field(
        default=...,
        description="Database password",
        validation_alias="DATABASE_PASSWORD"
    )
    host_rw: str = Field(
        default=...,
        description="Database host read/write",
        validation_alias="DATABASE_HOST_RW"
    )
    host_ro: str | None = Field(
        default=None,
        description="Database host read only",
        validation_alias="DATABASE_HOST_RO"
    )
    port: int = Field(
        default=5432,
        description="Database port",
        validation_alias="DATABASE_PORT"
    )
    database: str = Field(
        default="postgres",
        description="Database name",
        validation_alias="DATABASE_NAME"
    )
    pool_size: int = Field(
        default=10,
        description="Database pool size",
        validation_alias="DATABASE_POOL_SIZE"
    )
    max_overflow: int = Field(
        default=20,
        description="Database max overflow",
        validation_alias="DATABASE_MAX_OVERFLOW"
    )
    pool_recycle_seconds: int = Field(
        default=300,
        description="Database pool recycle seconds",
        validation_alias="DATABASE_POOL_RECYCLE_SECONDS"
    )
    pool_timeout_seconds: int = Field(
        default=30,
        description="Database pool timeout seconds",
        validation_alias="DATABASE_POOL_TIMEOUT_SECONDS"
    )
    pool_pre_ping: bool = Field(
        default=True,
        description="Database pool pre ping",
        validation_alias="DATABASE_POOL_PRE_PING"
    )
    echo_sql: DatabasePostgresEcho = Field(
        default=DatabasePostgresEcho.DISABLED,
        description="Database echo SQL",
        validation_alias="DATABASE_ECHO_SQL"
    )
    
    @property
    def cluster_mode(self) -> bool:
        """Cluster mode."""
        return self.host_ro is not None

    def _build_url(self, host: str) -> URL:
        return URL.create(
            drivername=f"{self.dialect}+{self.driver}",
            username=self.username,
            password=self.password,
            host=host,
            port=self.port,
            database=self.database,
        )
                
    def build_rw_uri(self) -> URL:
        """Build the database URI."""
        return self._build_url(self.host_rw)
        
    def build_ro_uri(self) -> URL:
        """Build the database URI."""
        if self.host_ro is None:
            raise ValueError("Host read only is not set")
        return self._build_url(self.host_ro)
    
    def __init_subclass__(cls, host_alias: str | None, **kwargs: Any) -> None:
        """Initialize subclass with custom validation prefix."""
        if host_alias is not None:
            for field_name, field_info in cls.model_fields.items():
                if hasattr(field_info, 'validation_alias'):
                    field_info.validation_alias = f"DATABASE_{host_alias.upper()}_{field_name.upper()}"
        
        super().__init_subclass__(**kwargs)


def create_database_postgresql_settings(host_alias: str | None) -> type[DatabasePostgreSQLSettings]:
    """Factory function to create database settings with custom prefix."""
    
    class CustomDatabasePostgreSQLSettings(DatabasePostgreSQLSettings, host_alias=host_alias):
        pass
    
    return CustomDatabasePostgreSQLSettings
