from unittest.mock import patch
import os

import pytest
from pydantic import ValidationError
from sqlalchemy.engine import URL

from solkit.database.sql.constants import DatabaseSQLEcho
from solkit.database.sql.postgres.settings import (
    create_database_postgres_settings,
    DatabasePostgresSettings
)

def test_database_postgresql_settings_with_minimal_required_fields_then_return_correct_values() -> None:
    """Test that default values are set correctly."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost"
    }
    with patch.dict(os.environ, environment_variables):
        # act
        settings = DatabasePostgresSettings()
        
    # assert
    assert settings.driver == "asyncpg"
    assert settings.dialect == "postgresql"
    assert settings.username == "testuser"
    assert settings.password == "testpass" # noqa: S105 # nosec
    assert settings.host_rw == "localhost"
    assert settings.host_ro is None
    assert settings.port == 5432
    assert settings.name == "postgres"
    assert settings.pool_size == 10
    assert settings.max_overflow == 20
    assert settings.pool_recycle_seconds == 300
    assert settings.pool_timeout_seconds == 30
    assert settings.pool_pre_ping is True
    assert settings.echo_sql == DatabaseSQLEcho.DISABLED
    assert settings.echo_pool == DatabaseSQLEcho.DISABLED


@pytest.mark.parametrize("environment_variable, missing_field", [
    pytest.param("DATABASE_USERNAME", "username", id="missing username"),
    pytest.param("DATABASE_PASSWORD", "password", id="missing password"),
    pytest.param("DATABASE_HOST_RW",  "host_rw",  id="missing host_rw"),
])
def test_database_postgresql_settings_with_missing_required_fields_then_raise_validation_error(
    environment_variable: str, 
    missing_field: str
) -> None:
    """Test that required fields raise ValidationError when missing."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost"
    }
    del environment_variables[environment_variable]
    
    # act
    with patch.dict(os.environ, environment_variables), pytest.raises(ValidationError) as exc_info:
        DatabasePostgresSettings()
        
        # assert
        assert missing_field in str(exc_info.value)


def test_database_postgresql_settings_with_environment_variable_aliases_then_return_correct_values() -> None:
    """Test that environment variable aliases work correctly."""
    # arrange
    environment_variables = {
        "DATABASE_DRIVER": "psycopg2",
        "DATABASE_DIALECT": "postgresql",
        "DATABASE_USERNAME": "envuser",
        "DATABASE_PASSWORD": "envpass",
        "DATABASE_HOST_RW": "envhost",
        "DATABASE_HOST_RO": "envrohost",
        "DATABASE_PORT": "5433",
        "DATABASE_NAME": "envdb",
        "DATABASE_POOL_SIZE": "15",
        "DATABASE_MAX_OVERFLOW": "25",
        "DATABASE_POOL_RECYCLE_SECONDS": "600",
        "DATABASE_POOL_TIMEOUT_SECONDS": "45",
        "DATABASE_POOL_PRE_PING": "false",
        "DATABASE_ECHO_SQL": "false",
        "DATABASE_ECHO_POOL": "false"
    }
    
    with patch.dict(os.environ, environment_variables):
        # act
        settings = DatabasePostgresSettings()
        
    # assert
    assert settings.driver == "psycopg2"
    assert settings.dialect == "postgresql"
    assert settings.username == "envuser"
    assert settings.password == "envpass" # noqa: S105 # nosec
    assert settings.host_rw == "envhost"
    assert settings.host_ro == "envrohost"
    assert settings.port == 5433
    assert settings.name == "envdb"
    assert settings.pool_size == 15
    assert settings.max_overflow == 25
    assert settings.pool_recycle_seconds == 600
    assert settings.pool_timeout_seconds == 45
    assert settings.pool_pre_ping is False
    assert settings.echo_sql == DatabaseSQLEcho.DISABLED
    assert settings.echo_pool == DatabaseSQLEcho.DISABLED


@pytest.mark.parametrize("host_ro, cluster_mode", [
    pytest.param(None,                 False, id="Without Readonly Host"),
    pytest.param("readonly.localhost", True,  id="With Readonly Host"),
])
def test_database_postgresql_settings_cluster_mode_property(host_ro: str | None, cluster_mode: bool) -> None:
    """Test cluster_mode property returns True when host_ro is set."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost",
    }
    if host_ro is not None:
        environment_variables["DATABASE_HOST_RO"] = host_ro
        
    # act
    with patch.dict(os.environ, environment_variables):
        settings = DatabasePostgresSettings()
        
    # assert
    assert settings.cluster_mode is cluster_mode



def test_database_postgresql_settings_build_rw_uri_then_return_correct_uri() -> None:
    """Test build_rw_uri method returns correct URL."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost",
        "DATABASE_PORT": "5433",
        "DATABASE_NAME": "testdb"
    }
    with patch.dict(os.environ, environment_variables):
        settings = DatabasePostgresSettings()
        
    # act
    url = settings.build_rw_uri()
    
    # assert
    assert isinstance(url, URL)
    assert url.drivername == "postgresql+asyncpg"
    assert url.username == "testuser"
    assert url.password == "testpass" # noqa: S105 # nosec
    assert url.host == "localhost"
    assert url.port == 5433
    assert url.database == "testdb"


def test_database_postgresql_settings_build_ro_uri_then_return_correct_uri() -> None:
    """Test build_ro_uri method returns correct URL when host_ro is set."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass", # nosec
        "DATABASE_HOST_RW": "localhost",
        "DATABASE_HOST_RO": "readonly.localhost",
        "DATABASE_PORT": "5433",
        "DATABASE_NAME": "testdb"
    }
    with patch.dict(os.environ, environment_variables):
        settings = DatabasePostgresSettings()
        
    # act
    url = settings.build_ro_uri()
    
    # assert
    assert isinstance(url, URL)
    assert url.drivername == "postgresql+asyncpg"
    assert url.username == "testuser"
    assert url.password == "testpass" # noqa: S105 # nosec
    assert url.host == "readonly.localhost"
    assert url.port == 5433
    assert url.database == "testdb"


def test_database_postgresql_settings_build_ro_uri_with_missing_readonly_host_then_raise_value_error() -> None:
    """Test build_ro_uri method raises ValueError when host_ro is not set."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost"
    }
    with patch.dict(os.environ, environment_variables):
        settings = DatabasePostgresSettings()
        
    # act & assert
    with pytest.raises(ValueError, match="Host read only is not set"):
        settings.build_ro_uri()


@pytest.mark.parametrize("echo_sql", [
    pytest.param(DatabaseSQLEcho.DISABLED, id="disabled"),
    pytest.param(DatabaseSQLEcho.ENABLED,  id="enabled"),
    pytest.param(DatabaseSQLEcho.DEBUG,    id="debug")
])
def test_database_postgresql_settings_echo_sql_then_return_correct_echo_sql(echo_sql: DatabaseSQLEcho) -> None:
    """Test echo_sql property returns correct value."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost",
        "DATABASE_ECHO_SQL": str(echo_sql.value).lower()
    }
    with patch.dict(os.environ, environment_variables):
        # act
        settings = DatabasePostgresSettings()
        
    # assert
    assert settings.echo_sql == echo_sql


@pytest.mark.parametrize("echo_pool", [
    pytest.param(DatabaseSQLEcho.DISABLED, id="disabled"),
    pytest.param(DatabaseSQLEcho.ENABLED,  id="enabled"),
    pytest.param(DatabaseSQLEcho.DEBUG,    id="debug")
])
def test_database_postgresql_settings_echo_pool_then_return_correct_echo_pool(echo_pool: DatabaseSQLEcho) -> None:
    """Test echo_pool property returns correct value."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost",
        "DATABASE_ECHO_POOL": str(echo_pool.value)
    }
    # act
    with patch.dict(os.environ, environment_variables):
        settings = DatabasePostgresSettings()
        
    # assert
    assert settings.echo_pool == echo_pool


def test_create_database_postgres_settings_without_host_alias_then_return_default_validation_aliases() -> None:
    """Test that create_database_postgres_settings without host_alias returns default validation aliases."""
    # arrange
    host_alias = None
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost"
    }
    
    # act
    CustomSettings = create_database_postgres_settings(host_alias)
    with patch.dict(os.environ, environment_variables):
        settings = CustomSettings()
    
    # assert
    assert issubclass(CustomSettings, DatabasePostgresSettings)
    assert settings.username == "testuser"
    assert settings.password == "testpass" # noqa: S105 # nosec
    assert settings.host_rw == "localhost"


def test_create_database_postgres_settings_with_host_alias_then_return_default_validation_aliases_with_custom_prefix() -> None:
    """Test that create_database_postgres_settings with host_alias returns default validation aliases with custom prefix."""
    # arrange
    host_alias = "self"
    environment_variables = {
        f"DATABASE_{host_alias.upper()}_USERNAME": "testuser",
        f"DATABASE_{host_alias.upper()}_PASSWORD": "testpass",
        f"DATABASE_{host_alias.upper()}_HOST_RW": "localhost"
    }
    
    # act
    CustomSettings = create_database_postgres_settings(host_alias)
    with patch.dict(os.environ, environment_variables):
        settings = CustomSettings()
        
    # assert
    assert issubclass(CustomSettings, DatabasePostgresSettings)
    assert settings.username == "testuser"
    assert settings.password == "testpass" # noqa: S105 # nosec
    assert settings.host_rw == "localhost"
