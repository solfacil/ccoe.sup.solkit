from unittest.mock import patch
import os

import pytest
from pydantic import ValidationError
from sqlalchemy.engine import URL

from solkit.database.sql.postgres.constants import DatabasePostgresEcho
from solkit.database.sql.postgres.settings import (
    DatabasePostgreSQLSettings,
    create_database_postgresql_settings,
)


def test_database_postgresql_settings_should_set_correct_default_values() -> None:
    """Test that default values are set correctly."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost"
    }
    with patch.dict(os.environ, environment_variables):
        # act
        settings = DatabasePostgreSQLSettings()
        
    # assert
    assert settings.driver == "asyncpg"
    assert settings.dialect == "postgresql"
    assert settings.username == "testuser"
    assert settings.password == "testpass" # noqa: S105 # nosec
    assert settings.host_rw == "localhost"
    assert settings.host_ro is None
    assert settings.port == 5432
    assert settings.database == "postgres"
    assert settings.pool_size == 10
    assert settings.max_overflow == 20
    assert settings.pool_recycle_seconds == 300
    assert settings.pool_timeout_seconds == 30
    assert settings.pool_pre_ping is True
    assert settings.echo_sql == DatabasePostgresEcho.DISABLED


def test_database_postgresql_settings_should_raise_validation_error_when_required_fields_missing() -> None:
    """Test that required fields raise ValidationError when missing."""
    # arrange & act & assert
    with pytest.raises(ValidationError) as exc_info:
        DatabasePostgreSQLSettings()
    
    errors = exc_info.value.errors()
    required_fields = ["username", "password", "host_rw"]
    
    for field in required_fields:
        assert any(field in str(error) for error in errors)


def test_database_postgresql_settings_should_use_environment_variable_aliases_correctly() -> None:
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
        "DATABASE_ECHO_SQL": "ENABLED"
    }
    
    with patch.dict(os.environ, environment_variables):
        # act
        settings = DatabasePostgreSQLSettings()
        
    # assert
    assert settings.driver == "psycopg2"
    assert settings.dialect == "postgresql"
    assert settings.username == "envuser"
    assert settings.password == "envpass" # noqa: S105 # nosec
    assert settings.host_rw == "envhost"
    assert settings.host_ro == "envrohost"
    assert settings.port == 5433
    assert settings.database == "envdb"
    assert settings.pool_size == 15
    assert settings.max_overflow == 25
    assert settings.pool_recycle_seconds == 600
    assert settings.pool_timeout_seconds == 45
    assert settings.pool_pre_ping is False
    assert settings.echo_sql == DatabasePostgresEcho.ENABLED


def test_cluster_mode_property_should_return_true_when_readonly_host_is_set() -> None:
    """Test cluster_mode property returns True when host_ro is set."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost",
        "DATABASE_HOST_RO": "readonly.localhost"
    }
    with patch.dict(os.environ, environment_variables):
        settings = DatabasePostgreSQLSettings()
        
    # act & assert
    assert settings.cluster_mode is True


def test_cluster_mode_property_should_return_false_when_readonly_host_is_not_set() -> None:
    """Test cluster_mode property returns False when host_ro is not set."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost"
    }
    with patch.dict(os.environ, environment_variables):
        settings = DatabasePostgreSQLSettings()
        
    # act & assert
    assert settings.cluster_mode is False


def test_build_rw_uri_should_return_correct_sqlalchemy_url() -> None:
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
        settings = DatabasePostgreSQLSettings()
        
    # act
    url = settings.build_rw_uri()
    
    # assert
    assert isinstance(url, URL)
    assert url.drivername == "asyncpg+postgresql"
    assert url.username == "testuser"
    assert url.password == "testpass" # noqa: S105 # nosec
    assert url.host == "localhost"
    assert url.port == 5433
    assert url.database == "testdb"


def test_build_ro_uri_should_return_correct_url_when_readonly_host_is_set() -> None:
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
        settings = DatabasePostgreSQLSettings()
        
    # act
    url = settings.build_ro_uri()
    
    # assert
    assert isinstance(url, URL)
    assert url.drivername == "asyncpg+postgresql"
    assert url.username == "testuser"
    assert url.password == "testpass" # noqa: S105 # nosec
    assert url.host == "readonly.localhost"
    assert url.port == 5433
    assert url.database == "testdb"


def test_build_ro_uri_should_raise_value_error_when_readonly_host_is_not_set() -> None:
    """Test build_ro_uri method raises ValueError when host_ro is not set."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost"
    }
    with patch.dict(os.environ, environment_variables):
        settings = DatabasePostgreSQLSettings()
        
    # act & assert
    with pytest.raises(ValueError, match="Host read only is not set"):
        settings.build_ro_uri()


def test_build_url_should_use_custom_driver_and_dialect_combination() -> None:
    """Test _build_url method with custom driver and dialect."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost"
    }
    with patch.dict(os.environ, environment_variables):
        settings = DatabasePostgreSQLSettings()
        settings.driver = "psycopg2"
        settings.dialect = "postgresql"
        
    # act
    url = settings.build_rw_uri()
    
    # assert
    assert url.drivername == "psycopg2+postgresql"


def test_subclass_with_host_alias_should_modify_validation_aliases() -> None:
    """Test that subclass with host_alias modifies validation aliases."""
    # arrange
    host_alias = "TEST"
    environment_variables = {
        f"DATABASE_{host_alias}_USERNAME": "testuser",
        f"DATABASE_{host_alias}_PASSWORD": "testpass",
        f"DATABASE_{host_alias}_HOST_RW": "localhost",
        f"DATABASE_{host_alias}_HOST_RO": "readonly.localhost"
    }
    class TestSettings(DatabasePostgreSQLSettings, host_alias=host_alias):
        pass
        
    # act
    with patch.dict(os.environ, environment_variables):
        settings = TestSettings()
        
    # assert
    assert settings.username == "testuser"
    assert settings.password == "testpass" # noqa: S105 # nosec
    assert settings.host_rw == "localhost"
    assert settings.host_ro == "readonly.localhost"
    

def test_subclass_without_host_alias_should_use_default_validation_aliases() -> None:
    """Test that subclass without host_alias uses default validation aliases."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost"
    }
    class TestSettings(DatabasePostgreSQLSettings, host_alias=None):
        pass
        
    # act
    with patch.dict(os.environ, environment_variables):
        settings = TestSettings()
        
    # assert
    assert settings.username == "testuser"
    assert settings.password == "testpass" # noqa: S105 # nosec
    assert settings.host_rw == "localhost"


def test_create_database_postgresql_settings_factory_should_create_class_with_custom_host_alias() -> None:
    """Test factory function creates settings class with custom host alias."""
    # arrange
    host_alias = "custom"
    
    # act
    CustomSettings = create_database_postgresql_settings(host_alias)
    
    # assert
    assert issubclass(CustomSettings, DatabasePostgreSQLSettings)
    
    # Test that the custom class works with modified aliases
    with patch.dict(os.environ, {
        "DATABASE_CUSTOM_USERNAME": "testuser",
        "DATABASE_CUSTOM_PASSWORD": "testpass",
        "DATABASE_CUSTOM_HOST_RW": "localhost"
    }):
        settings = CustomSettings()
        
    assert settings.username == "testuser"
    assert settings.password == "testpass" # noqa: S105 # nosec
    assert settings.host_rw == "localhost"


def test_create_database_postgresql_settings_factory_should_create_class_without_host_alias() -> None:
    """Test factory function creates settings class without host alias."""
    # arrange
    host_alias = None
    
    # act
    CustomSettings = create_database_postgresql_settings(host_alias)
    
    # assert
    assert issubclass(CustomSettings, DatabasePostgreSQLSettings)
    
    # Test that the custom class works with default aliases
    with patch.dict(os.environ, {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost"
    }):
        settings = CustomSettings()
        
    assert settings.username == "testuser"
    assert settings.password == "testpass" # noqa: S105 # nosec
    assert settings.host_rw == "localhost"


def test_factory_function_should_create_unique_classes_for_different_aliases() -> None:
    """Test that factory function creates unique classes for different aliases."""
    # arrange
    alias1 = "first"
    alias2 = "second"
    
    # act
    Settings1 = create_database_postgresql_settings(alias1)
    Settings2 = create_database_postgresql_settings(alias2)
    
    # assert
    assert Settings1 is not Settings2
    assert Settings1.__name__ != Settings2.__name__


def test_database_postgresql_settings_should_raise_validation_error_for_invalid_port_type() -> None:
    """Test that invalid port type raises ValidationError."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost",
        "DATABASE_PORT": "invalid_port"
    }
    
    # act
    with patch.dict(os.environ, environment_variables), pytest.raises(ValidationError) as exc_info:
        DatabasePostgreSQLSettings()
    
    # assert
    errors = exc_info.value.errors()
    assert any("port" in str(error) for error in errors)


def test_database_postgresql_settings_should_raise_validation_error_for_invalid_pool_size_type() -> None:
    """Test that invalid pool_size type raises ValidationError."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost",
        "DATABASE_POOL_SIZE": "invalid_size"
    }
    
    # act
    with patch.dict(os.environ, environment_variables), pytest.raises(ValidationError) as exc_info:
        DatabasePostgreSQLSettings()
    
    # assert
    errors = exc_info.value.errors()
    assert any("pool_size" in str(error) for error in errors)


def test_database_postgresql_settings_should_raise_validation_error_for_invalid_echo_sql_value() -> None:
    """Test that invalid echo_sql value raises ValidationError."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost",
        "DATABASE_ECHO_SQL": "INVALID_VALUE"
    }
    
    # act
    with patch.dict(os.environ, environment_variables), pytest.raises(ValidationError) as exc_info:
        DatabasePostgreSQLSettings()
    
    # assert
    errors = exc_info.value.errors()
    assert any("echo_sql" in str(error) for error in errors)


def test_database_postgresql_settings_should_validate_boolean_fields_from_string_representations() -> None:
    """Test that boolean fields properly validate string representations."""
    # arrange
    with patch.dict(os.environ, {
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_HOST_RW": "localhost",
        "DATABASE_POOL_PRE_PING": "false"
    }):
        # act
        settings = DatabasePostgreSQLSettings()
        
    # assert
    assert settings.pool_pre_ping is False


def test_database_postgresql_settings_should_raise_validation_error_for_empty_strings_in_required_fields() -> None:
    """Test that empty strings for required fields raise ValidationError."""
    # arrange
    environment_variables = {
        "DATABASE_USERNAME": "",
        "DATABASE_PASSWORD": "",
        "DATABASE_HOST_RW": ""
    }
    
    # act
    with patch.dict(os.environ, environment_variables), pytest.raises(ValidationError) as exc_info:
        DatabasePostgreSQLSettings()
    
    # assert
    errors = exc_info.value.errors()
    required_fields = ["username", "password", "host_rw"]
    for field in required_fields:
        assert any(field in str(error) for error in errors)
