import logging
from enum import Enum, StrEnum

# Pagination Default
DATABASE_DEFAULT_SORT_COLUMN = 'id'
DATABASE_DEFAULT_SORT_TYPE = 'desc'
DATABASE_DEFAULT_PAGE_SIZE = 100
DATABASE_DEFAULT_OFFSET = 0


class DatabasePostgresEcho(Enum):
    """Database PostgreSQL echo."""
    
    DEBUG = logging.DEBUG
    ENABLED = logging.INFO
    DISABLED = logging.WARNING


class DatabasePostgresSessionType(StrEnum):
    """Database PostgreSQL session type."""
    
    READ_WRITE = "rw"
    READ_ONLY = "ro"


class DatabasePostgresSortType(StrEnum):
    """Database PostgreSQL sort type."""
    
    ASC = "asc"
    DESC = "desc"
