from enum import StrEnum


class Environment(StrEnum):
    """Environment constants."""

    PRD = 'prd'
    STG = 'stg'
    DEV = 'dev'
    LOCAL = 'local'
