import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from solkit.cache.constants import CacheDeploymentMode
from solkit.cache.settings import (
    CacheModeSettings,
    CacheRedisClusterSettings,
    CacheRedisSettings,
    CacheRedisSingleNodeSettings,
)


@pytest.mark.parametrize(
    'deployment_mode',
    [
        pytest.param(CacheDeploymentMode.CLUSTER, id='cluster'),
        pytest.param(CacheDeploymentMode.SINGLE, id='single'),
    ],
)
def test_valid_deployment_mode(deployment_mode: CacheDeploymentMode) -> None:
    """Test that valid deployment modes are accepted."""
    # arrange
    with patch.dict(os.environ, {'CACHE_DEPLOYMENT_MODE': deployment_mode.value}):
        # act
        settings = CacheModeSettings()
    # assert
    assert settings.deployment_mode == deployment_mode


def test_invalid_deployment_mode() -> None:
    """Test that invalid deployment mode raises ValidationError."""
    # arrange
    environment_variables = {'CACHE_DEPLOYMENT_MODE': 'invalid_mode'}
    with patch.dict(os.environ, environment_variables), pytest.raises(ValidationError):
        # act
        CacheModeSettings()


def test_valid_settings_with_defaults() -> None:
    """Test that valid settings with defaults work correctly."""
    # arrange
    with patch.dict(
        os.environ, {'CACHE_DEPLOYMENT_MODE': CacheDeploymentMode.CLUSTER.value, 'CACHE_HOST': 'localhost'}
    ):
        # act
        settings = CacheRedisSettings()
    # assert
    assert settings.deployment_mode == CacheDeploymentMode.CLUSTER
    assert settings.host == 'localhost'
    assert settings.port == 6379
    assert settings.max_connections == 10
    assert settings.socket_timeout == 5
    assert settings.socket_connect_timeout == 5
    assert settings.socket_keepalive is True
    assert settings.health_check_interval == 10
    assert settings.retry_max_attempts == 3


def test_build_uri_property() -> None:
    """Test the build_uri property returns correct URI format."""
    # arrange
    environment_variables = {
        'CACHE_DEPLOYMENT_MODE': CacheDeploymentMode.CLUSTER.value,
        'CACHE_HOST': 'redis.example.com',
        'CACHE_PORT': '6380',
        'CACHE_DB': '0',
    }

    with patch.dict(os.environ, environment_variables):
        # act
        settings = CacheRedisSettings()
    # assert
    expected_uri = 'redis://redis.example.com:6380/0'
    assert settings.build_uri == expected_uri


def test_valid_cluster_settings_with_defaults() -> None:
    """Test that valid cluster settings with defaults work correctly."""
    # arrange
    environment_variables = {
        'CACHE_DEPLOYMENT_MODE': CacheDeploymentMode.CLUSTER.value,
        'CACHE_HOST': 'redis.example.com',
        'CACHE_PORT': '6380',
        # 'CACHE_DB': '0',
    }
    with patch.dict(os.environ, environment_variables):
        # act
        settings = CacheRedisClusterSettings()
    # assert
    assert settings.deployment_mode == CacheDeploymentMode.CLUSTER
    assert settings.host == 'redis.example.com'
    assert settings.port == 6380
    assert settings.db == 0
    assert settings.read_from_replicas is True
    assert settings.require_full_coverage is False


def test_valid_single_node_settings_with_defaults() -> None:
    """Test that valid single node settings with defaults work correctly."""
    # arrange
    environment_variables = {'CACHE_DEPLOYMENT_MODE': CacheDeploymentMode.SINGLE.value, 'CACHE_HOST': 'localhost'}
    with patch.dict(os.environ, environment_variables):
        # act
        settings = CacheRedisSingleNodeSettings()
    # assert
    assert settings.deployment_mode == CacheDeploymentMode.SINGLE
    assert settings.host == 'localhost'
    assert settings.port == 6379
    assert settings.retry_on_timeout is True
