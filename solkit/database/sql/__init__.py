"""SQL Database."""

from .abstracts import DatabaseSQLAdapterAbstract
from .orm.model import EntityModel
from .postgres.adapter import DatabasePostgresAdapter
from .protocols import DatabaseSQLRepositoryProtocol
from .repository import DatabaseSQLRepository
# from .sqlite.adapter import DatabaseSQLiteAdapter

__all__ = [
    # Abstracts
    "DatabaseSQLAdapterAbstract",
    "DatabaseSQLRepositoryProtocol",
    # Common for SQLAlchemy
    "DatabaseSQLRepository",
    "EntityModel",
    # Adapters
    "DatabasePostgresAdapter",
    # "DatabaseSQLiteAdapter",
]
