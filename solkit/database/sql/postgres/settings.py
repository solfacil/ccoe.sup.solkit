from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL

from ..constants import DATABASE_SETTINGS_PREFIX, DatabaseSQLEcho


class DatabasePostgresSettings(BaseSettings):
    """Database PostgreSQL settings."""

    driver: str = Field(
        default='asyncpg', description='Database driver', validation_alias=f'{DATABASE_SETTINGS_PREFIX}_DRIVER'
    )
    dialect: str = Field(
        default='postgresql', description='Database dialect', validation_alias=f'{DATABASE_SETTINGS_PREFIX}_DIALECT'
    )
    username: str = Field(
        default=..., description='Database username', validation_alias=f'{DATABASE_SETTINGS_PREFIX}_USERNAME'
    )
    password: str = Field(
        default=..., description='Database password', validation_alias=f'{DATABASE_SETTINGS_PREFIX}_PASSWORD'
    )
    host_rw: str = Field(
        default=..., description='Database host read/write', validation_alias=f'{DATABASE_SETTINGS_PREFIX}_HOST_RW'
    )
    host_ro: str | None = Field(
        default=None, description='Database host read only', validation_alias=f'{DATABASE_SETTINGS_PREFIX}_HOST_RO'
    )
    port: int = Field(default=5432, description='Database port', validation_alias=f'{DATABASE_SETTINGS_PREFIX}_PORT')
    name: str = Field(
        default='postgres', description='Database name', validation_alias=f'{DATABASE_SETTINGS_PREFIX}_NAME'
    )
    pool_size: int = Field(
        default=10, description='Database pool size', validation_alias=f'{DATABASE_SETTINGS_PREFIX}_POOL_SIZE'
    )
    max_overflow: int = Field(
        default=20, description='Database max overflow', validation_alias=f'{DATABASE_SETTINGS_PREFIX}_MAX_OVERFLOW'
    )
    pool_recycle_seconds: int = Field(
        default=300,
        description='Database pool recycle seconds',
        validation_alias=f'{DATABASE_SETTINGS_PREFIX}_POOL_RECYCLE_SECONDS',
    )
    pool_timeout_seconds: int = Field(
        default=30,
        description='Database pool timeout seconds',
        validation_alias=f'{DATABASE_SETTINGS_PREFIX}_POOL_TIMEOUT_SECONDS',
    )
    pool_pre_ping: bool = Field(
        default=True, description='Database pool pre ping', validation_alias=f'{DATABASE_SETTINGS_PREFIX}_POOL_PRE_PING'
    )
    echo_sql: str | DatabaseSQLEcho = Field(
        default=DatabaseSQLEcho.DISABLED,
        description='Database echo SQL',
        validation_alias=f'{DATABASE_SETTINGS_PREFIX}_ECHO_SQL',
    )
    echo_pool: str | DatabaseSQLEcho = Field(
        default=DatabaseSQLEcho.DISABLED,
        description='Database echo pool',
        validation_alias=f'{DATABASE_SETTINGS_PREFIX}_ECHO_POOL',
    )
    connection_timeout_seconds: int = Field(
        default=10,
        description='Database connection timeout seconds',
        validation_alias=f'{DATABASE_SETTINGS_PREFIX}_CONNECTION_TIMEOUT_SECONDS',
    )
    # statement_timeout_ms: int = Field(
    #     default=30,
    #     description="Database statement timeout seconds",
    #     validation_alias=f"{DATABASE_SETTINGS_PREFIX}_STATEMENT_TIMEOUT_MS"
    # )

    @property
    def cluster_mode(self) -> bool:
        """Cluster mode."""
        return self.host_ro is not None

    def _build_url(self, host: str) -> URL:
        return URL.create(
            drivername=f'{self.dialect}+{self.driver}',
            username=self.username,
            password=self.password,
            host=host,
            port=self.port,
            database=self.name,
        )

    def build_rw_uri(self) -> URL:
        """Build the database URI."""
        return self._build_url(self.host_rw)

    def build_ro_uri(self) -> URL:
        """Build the database URI."""
        if self.host_ro is None:
            raise ValueError('Host read only is not set')
        return self._build_url(self.host_ro)

    def __init_subclass__(cls, host_alias: str | None, **kwargs) -> None:  # type: ignore  # noqa: ANN003
        """Initialize subclass with custom validation prefix."""
        if host_alias is not None:
            prefix = f'{DATABASE_SETTINGS_PREFIX}_{host_alias.upper()}'

            for field_name, field_info in cls.model_fields.items():
                if hasattr(field_info, 'validation_alias'):
                    field_info.validation_alias = f'{prefix}_{field_name.upper()}'

        super().__init_subclass__(**kwargs)

    @field_validator('echo_sql', 'echo_pool', mode='before')
    @classmethod
    def validate_echo(cls, value: str | DatabaseSQLEcho) -> DatabaseSQLEcho:
        """Validate echo."""
        if isinstance(value, DatabaseSQLEcho):
            return value
        value = value.lower()
        values = {
            'true': DatabaseSQLEcho.ENABLED,
            'false': DatabaseSQLEcho.DISABLED,
            'debug': DatabaseSQLEcho.DEBUG,
        }
        if value not in values:
            raise ValueError('Invalid echo')
        return values[value]


def create_database_postgres_settings(host_alias: str | None) -> type[DatabasePostgresSettings]:
    """Factory function to create database settings with custom prefix."""

    class CustomDatabasePostgresSettings(DatabasePostgresSettings, host_alias=host_alias):
        pass

    return CustomDatabasePostgresSettings
