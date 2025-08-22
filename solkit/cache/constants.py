from enum import StrEnum

CACHE_SETTINGS_PREFIX = "CACHE"
CACHE_PROTOCOL = "redis://"


class CacheDeploymentMode(StrEnum):
    """Cache deployment mode."""
    
    CLUSTER = "cluster"
    SINGLE = "single"
