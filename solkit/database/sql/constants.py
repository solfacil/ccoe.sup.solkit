from enum import Enum, StrEnum

# Settings Prefix
DATABASE_SETTINGS_PREFIX = "DATABASE"

# Pagination Default
DATABASE_DEFAULT_SORT_COLUMN = "id"
DATABASE_DEFAULT_SORT_TYPE = "desc"
DATABASE_DEFAULT_PAGE_SIZE = 100
DATABASE_DEFAULT_OFFSET = 0

# Healthcheck Query
DATABASE_HEALTHCHECK_QUERY = "SELECT 1"

# Indexes Naming Convention
DATABASE_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}


class DatabaseSQLEcho(Enum):
    """Database PostgreSQL echo."""
    
    DEBUG = "debug"
    ENABLED = True
    DISABLED = False


class DatabaseSQLSession(StrEnum):
    """Database SQL session type."""
    
    READ_WRITE = "rw"
    READ_ONLY = "ro"


class DatabaseSQLSort(StrEnum):
    """Database SQL sort type."""
    
    ASC = "asc"
    DESC = "desc"
