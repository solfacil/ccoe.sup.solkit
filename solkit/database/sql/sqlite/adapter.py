

from .settings import DatabaseSQLiteSettings, create_database_sqlite_settings


class DatabaseSQLiteAdapter:
    """Database SQLite adapter."""
    
    @classmethod
    def config(cls, application_alias: str, host_alias: str = "self") -> "DatabaseSQLiteAdapter":
        """Config the database cluster."""
        settings = create_database_sqlite_settings(host_alias)
        return cls(settings())
    
    def __init__(self, settings: DatabaseSQLiteSettings) -> None:
        """Initialize the database adapter."""
        self._settings = settings
