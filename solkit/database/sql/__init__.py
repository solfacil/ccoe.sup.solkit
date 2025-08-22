"""SQL Database module."""

from .abstracts import DatabaseSQLAdapterAbstract
from .constants import DatabaseSQLSession
from .orm.model import EntityModel
from .postgres.adapter import DatabasePostgresAdapter
from .protocols import DatabaseSQLRepositoryProtocol
from .repository import DatabaseSQLRepository

__all__ = [
    # Abstracts
    "DatabaseSQLAdapterAbstract",
    "DatabaseSQLRepositoryProtocol",
    # Common for SQLAlchemy
    "DatabaseSQLRepository",
    "EntityModel",
    # Constants
    "DatabaseSQLSession",
    # Adapters
    "DatabasePostgresAdapter",
]
