from enum import StrEnum

CACHE_PROTOCOL = "redis://"


class CacheDeploymentMode(StrEnum):
    """Cache deployment mode."""
    
    CLUSTER = "cluster"
    SINGLE = "single"
