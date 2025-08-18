import logging
from asyncio import current_task
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from .abstracts import DatabasePostgreSQLAdapterAbstract
from .constants import DatabasePostgresSessionType
from .settings import DatabasePostgreSQLSettings, create_database_postgresql_settings

logger = logging.getLogger(__name__)


class DatabasePostgreSQLAdapter:
    """Adapter for the database."""
    
    @classmethod
    def config(cls, host_alias: str = "self") -> "DatabasePostgreSQLAdapter":
        """Config the database cluster."""
        settings = create_database_postgresql_settings(host_alias)
        return cls(settings())

    def __init__(self, settings: DatabasePostgreSQLSettings) -> None:
        """Initialize the database adapter."""
        self._settings = settings
        self._async_engine_rw: AsyncEngine
        self._async_engine_ro: AsyncEngine
    
    @property
    def _async_engine_config(self) -> dict[str, Any]:
        return {
            "pool_size": self._settings.pool_size,
            "max_overflow": self._settings.max_overflow,
            "pool_timeout": self._settings.pool_timeout_seconds,
            "pool_pre_ping": self._settings.pool_pre_ping,
            "pool_recycle": self._settings.pool_recycle_seconds,
            "echo": self._settings.echo_sql,
        }

    def _create_async_engine(self, uri: URL) -> AsyncEngine:
        logger.info(f"[ADAPTER][DATABASE][ENGINE][URI: {uri.render_as_string(hide_password=True)}]")
        return create_async_engine(
            url=uri,
            **self._async_engine_config
        )
       
    def _async_session_facrory(self, async_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            autoflush=False,
            expire_on_commit=False,
            autocommit=False,
            future=True
        )
        
    async def connect(self) -> None:
        """Connect to the database."""
        self._async_engine_rw = self._create_async_engine(self._settings.build_rw_uri())
        if self._settings.cluster_mode:
            self._async_engine_ro = self._create_async_engine(self._settings.build_ro_uri())
    
    def _get_engine(self, session_type: DatabasePostgresSessionType) -> AsyncEngine:
        return (
            self._async_engine_rw 
            if session_type == DatabasePostgresSessionType.READ_WRITE 
            else self._async_engine_ro
        )
    
    @asynccontextmanager
    async def get_connection(
        self, 
        session_type: DatabasePostgresSessionType = DatabasePostgresSessionType.READ_WRITE
    ):
        """Get a connection from the database."""
        _engine = self._get_engine(session_type)
        
        async with _engine.connect() as connection, connection.begin():
            yield connection
    
    @asynccontextmanager
    async def get_session(
        self, 
        session_type: DatabasePostgresSessionType = DatabasePostgresSessionType.READ_WRITE
    ):
        """Get a session from the database."""
        _engine = self._get_engine(session_type)
        current_session = async_scoped_session(self._async_session_facrory(_engine), current_task)
        try:
            yield current_session()
            await current_session.commit()
        except Exception as err:
            logger.error(f"[ADAPTER][DATABASE][SESSION ROLLBACK][ERROR]: {err}")
            await current_session.rollback()
            raise
        finally:
            await current_session.remove()

    async def disconnect(self) -> None:
        """Disconnect from the database."""
        await self._async_engine_rw.dispose()
        if self._settings.cluster_mode:
            await self._async_engine_ro.dispose()
        
