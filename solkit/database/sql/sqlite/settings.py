from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSQLiteSettings(BaseSettings):
    """Database SQLite settings."""
    
    database_path: str = Field(
        default=":memory:",
        description="Database path",
        validation_alias="DATABASE_PATH"
    )
    
    def __init_subclass__(cls, host_alias: str | None, **kwargs: Any) -> None:
        """Initialize the database settings."""
        super().__init_subclass__(**kwargs)
        

def create_database_sqlite_settings(host_alias: str | None) -> type[DatabaseSQLiteSettings]:
    """Create the database settings."""
    
    class CustomDatabaseSQLiteSettings(DatabaseSQLiteSettings, host_alias=host_alias):
        pass
    
    return CustomDatabaseSQLiteSettings
