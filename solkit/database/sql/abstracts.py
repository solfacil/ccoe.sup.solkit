from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from sqlalchemy.engine.url import URL

from .constants import DatabaseSQLSession


class DatabaseSQLSettingsAbstract(ABC):
    """Abstract class for the database settings."""
    
    @property
    @abstractmethod
    def cluster_mode(self) -> bool:
        """Get the database cluster mode."""
        raise NotImplementedError()
    
    @abstractmethod
    def build_rw_uri(self) -> URL:
        """Build the database URI."""
        raise NotImplementedError()
    
    @abstractmethod
    def build_ro_uri(self) -> URL:
        """Build the database URI."""
        raise NotImplementedError()


class DatabaseSQLAdapterAbstract(ABC):
    """Abstract class for the database adapter."""
    
    @classmethod
    @abstractmethod
    def config(cls, host_alias: str = "self") -> "DatabaseSQLAdapterAbstract":
        """Config the database cluster."""
        raise NotImplementedError()
    
    @abstractmethod
    def __init__(self, settings: DatabaseSQLSettingsAbstract) -> None:
        """Initialize the database adapter."""
        raise NotImplementedError()
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the database."""
        raise NotImplementedError()
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the database."""
        raise NotImplementedError()
    
    @abstractmethod
    async def get_connection(
        self, 
        session_type: DatabaseSQLSession = DatabaseSQLSession.READ_WRITE
    ) -> AsyncGenerator:
        """Get a connection from the database."""
        raise NotImplementedError()
    
    @abstractmethod
    async def get_session(
        self, 
        session_type: DatabaseSQLSession = DatabaseSQLSession.READ_WRITE
    ) -> AsyncGenerator:
        """Get a session from the database."""
        raise NotImplementedError()
