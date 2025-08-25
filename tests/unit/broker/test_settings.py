from unittest.mock import patch

import pytest
from pydantic import ValidationError

from solkit.broker.constants import BrokerKafkaAcks
from solkit.broker.settings import (
    BrokerKafkaConsumerSettings,
    BrokerKafkaProducerSettings,
    BrokerKafkaSettings,
)

# Common variable for environment variable path
ENVIRONMENT_PATH: str = 'os.environ'
DEFAULT_KAFKA_BOOTSTRAP_SERVERS: str = 'localhost:9092'
DEFAULT_CONSUMER_SETTINGS: dict[str, str] = {
    'BROKER_BOOTSTRAP_SERVERS': DEFAULT_KAFKA_BOOTSTRAP_SERVERS,
    'BROKER_TOPICS': 'SOME-TOPIC,ANOTHER-TOPIC',
    'BROKER_GROUP_ID': 'unittest-group',
}
DEFAULT_PRODUCER_SETTINGS: dict[str, str] = {
    'BROKER_BOOTSTRAP_SERVERS': DEFAULT_KAFKA_BOOTSTRAP_SERVERS,
    'BROKER_ACKS': 'all',
}


def test_create_common_settings_with_valid_environment_variables() -> None:
    """Test creating settings with valid environment variables."""
    # arrange
    environment_variables = {'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092', 'BROKER_REQUEST_TIMEOUT_MS': '10000'}
    with patch.dict(ENVIRONMENT_PATH, environment_variables):
        # act
        settings = BrokerKafkaSettings()

    # assert
    assert settings.bootstrap_servers == 'localhost:9092'
    assert settings.request_timeout_ms == 10000


def test_create_common_settings_with_default_values() -> None:
    """Test creating settings with default values for optional fields."""
    # arrange
    environment_variables = {'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092'}
    with patch.dict(ENVIRONMENT_PATH, environment_variables):
        # act
        settings = BrokerKafkaSettings()

    # assert
    assert settings.bootstrap_servers == 'localhost:9092'
    assert settings.request_timeout_ms == 5000  # default value


def test_create_common_settings_with_missing_required_field() -> None:
    """Test that creating settings without required fields raises error."""
    # arrange & act & assert
    with pytest.raises(ValidationError):
        BrokerKafkaSettings()


def test_create_consumer_settings_with_minimum_environment_variables() -> None:
    """Test creating consumer settings with valid environment variables."""
    # arrange
    environment_variables = {
        'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092',
        'BROKER_TOPICS': 'TEST-TOPIC',
        'BROKER_GROUP_ID': 'test-group',
    }
    with patch.dict(ENVIRONMENT_PATH, environment_variables):
        # act
        settings = BrokerKafkaConsumerSettings()

    # assert
    assert settings.bootstrap_servers == 'localhost:9092'
    assert settings.topics == 'TEST-TOPIC'
    assert settings.group_id == 'test-group'
    assert not settings.enable_auto_commit
    assert settings.max_poll_records == 100
    assert settings.max_poll_interval_ms == 5 * 60 * 1000
    assert settings.heartbeat_interval_ms == 15 * 1000
    assert settings.session_timeout_ms == 90 * 1000
    assert settings.retry_max_times == 0


def test_create_consumer_settings_with_all_environment_variables() -> None:
    """Test creating consumer settings with all environment variables set."""
    # arrange
    environment_variables = {
        'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092',
        'BROKER_TOPICS': 'TEST-TOPIC,ANOTHER-TOPIC',
        'BROKER_GROUP_ID': 'test-group',
        'BROKER_ENABLE_AUTO_COMMIT': 'true',
        'BROKER_MAX_POLL_RECORDS': '200',
        'BROKER_MAX_POLL_INTERVAL_MS': '600000',
        'BROKER_HEARTBEAT_INTERVAL_MS': '30000',
        'BROKER_SESSION_TIMEOUT_MS': '120000',
        'BROKER_RETRY_MAX_TIMES': '2',
    }
    with patch.dict(ENVIRONMENT_PATH, environment_variables):
        # act
        settings = BrokerKafkaConsumerSettings()

    # assert
    assert settings.bootstrap_servers == 'localhost:9092'
    assert settings.topics == 'TEST-TOPIC,ANOTHER-TOPIC'
    assert settings.group_id == 'test-group'
    assert settings.enable_auto_commit
    assert settings.max_poll_records == 200
    assert settings.max_poll_interval_ms == 600000
    assert settings.heartbeat_interval_ms == 30000
    assert settings.session_timeout_ms == 120000
    assert settings.retry_max_times == 2


def test_consumer_settings_parse_topics() -> None:
    """Test parsing topics."""
    # arrange
    environment_variables = {
        'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092',
        'BROKER_TOPICS': 'TEST-TOPIC,ANOTHER-TOPIC',
        'BROKER_GROUP_ID': 'test-group',
    }
    with patch.dict(ENVIRONMENT_PATH, environment_variables):
        settings = BrokerKafkaConsumerSettings()
        # act
        parsed_topics = settings._parse_topics(settings.topics)

    # assert
    assert parsed_topics == ['TEST-TOPIC', 'ANOTHER-TOPIC']


def test_consumer_settings_generate_retry_topics() -> None:
    """Test generating retry topics."""
    # arrange
    retry_max_times = 2
    environment_variables = {
        'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092',
        'BROKER_TOPICS': 'SOME-TOPIC',
        'BROKER_GROUP_ID': 'test-group',
        'BROKER_RETRY_MAX_TIMES': str(retry_max_times),
    }
    with patch.dict(ENVIRONMENT_PATH, environment_variables):
        settings = BrokerKafkaConsumerSettings()
        # act
        retry_topics = settings._generate_retry_topics()

    # assert
    assert retry_topics == ['SOME-TOPIC-RETRY-1', 'SOME-TOPIC-RETRY-2']


def test_consumer_settings_generate_dead_letter_queue_topics() -> None:
    """Test generating dead letter queue topics."""
    # arrange
    environment_variables = {
        'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092',
        'BROKER_TOPICS': 'TEST-TOPIC,ANOTHER-TOPIC',
        'BROKER_GROUP_ID': 'test-group',
    }
    with patch.dict(ENVIRONMENT_PATH, environment_variables):
        # act
        settings = BrokerKafkaConsumerSettings()
    # assert
    assert settings.topics == 'TEST-TOPIC,ANOTHER-TOPIC'


def test_consumer_settings_get_topics_single_topic() -> None:
    """Test getting topics for a single topic."""
    # arrange
    environment_variables = {
        'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092',
        'BROKER_TOPICS': 'TEST-TOPIC',
        'BROKER_GROUP_ID': 'test-group',
    }
    with patch.dict(ENVIRONMENT_PATH, environment_variables):
        settings = BrokerKafkaConsumerSettings()

        # act
        topics = settings.get_topics()

    # assert
    expected_topics = ['TEST-TOPIC', 'TEST-TOPIC-DLQ']
    assert topics == expected_topics


def test_consumer_settings_get_topics_multiple_topics_with_retry() -> None:
    """Test getting topics for multiple topics with retry enabled."""
    # arrange
    environment_variables = {
        'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092',
        'BROKER_TOPICS': 'SOME-TOPIC,ANOTHER-TOPIC',
        'BROKER_GROUP_ID': 'test-group',
        'BROKER_RETRY_MAX_TIMES': '2',
    }
    with patch.dict(ENVIRONMENT_PATH, environment_variables):
        settings = BrokerKafkaConsumerSettings()

        # act
        topics = settings.get_topics()

    # assert
    expected_topics = [
        'SOME-TOPIC',
        'ANOTHER-TOPIC',  # original topics
        'SOME-TOPIC-DLQ',
        'ANOTHER-TOPIC-DLQ',  # dead letter queue topics
        'SOME-TOPIC-RETRY-1',
        'SOME-TOPIC-RETRY-2',  # retry topics for topic 1
        'ANOTHER-TOPIC-RETRY-1',
        'ANOTHER-TOPIC-RETRY-2',  # retry topics for topic 2
    ]
    assert topics == expected_topics


def test_consumer_settings_validate_topics_names_valid() -> None:
    """Test topic name validation with valid names."""
    # arrange
    environment_variables = {
        'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092',
        'BROKER_TOPICS': 'VALID-TOPIC-NAME',
        'BROKER_GROUP_ID': 'test-group',
    }
    with patch.dict(ENVIRONMENT_PATH, environment_variables):
        # act
        settings = BrokerKafkaConsumerSettings()

    # assert
    assert settings.topics == 'VALID-TOPIC-NAME'


def test_consumer_settings_validate_topics_names_invalid_lowercase() -> None:
    """Test topic name validation with invalid lowercase names."""
    # Arrange
    environment_variables = {
        'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092',
        'BROKER_TOPICS': 'invalid-topic-name',
        'BROKER_GROUP_ID': 'test-group',
    }
    with patch.dict(ENVIRONMENT_PATH, environment_variables), pytest.raises(ValidationError):
        # act
        BrokerKafkaConsumerSettings()


@pytest.mark.parametrize(
    'invalid_character',
    [
        pytest.param('_', id='underscore'),
        pytest.param('.', id='dot'),
        pytest.param(' ', id='space'),
        pytest.param('!', id='exclamation-mark'),
        pytest.param('@', id='at-sign'),
        pytest.param('#', id='hash'),
        pytest.param('$', id='dollar-sign'),
        pytest.param('%', id='percent'),
        pytest.param('^', id='caret'),
    ],
)
def test_consumer_settings_validate_topics_names_invalid_character(invalid_character: str) -> None:
    """Test topic name validation with invalid underscore names."""
    # Arrange
    environment_variables = {
        'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092',
        'BROKER_TOPICS': f'TOPIC-{invalid_character}',
        'BROKER_GROUP_ID': 'test-group',
    }
    with patch.dict(ENVIRONMENT_PATH, environment_variables), pytest.raises(ValidationError):
        # act
        BrokerKafkaConsumerSettings()


def test_consumer_settings_validate_topics_names_multiple_valid() -> None:
    """Test topic name validation with multiple valid names."""
    # arrange
    environment_variables = {
        'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092',
        'BROKER_TOPICS': 'SOME-TOPIC,ANOTHER-TOPIC',
        'BROKER_GROUP_ID': 'test-group',
    }
    with patch.dict(ENVIRONMENT_PATH, environment_variables):
        # act
        settings = BrokerKafkaConsumerSettings()

    # assert
    assert settings.topics == 'SOME-TOPIC,ANOTHER-TOPIC'


def test_consumer_settings_validate_topics_names_mixed_valid_invalid() -> None:
    """Test topic name validation with mixed valid and invalid names."""
    # arrange
    environment_variables = {
        'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092',
        'BROKER_TOPICS': 'VALID-TOPIC,invalid-topic',
        'BROKER_GROUP_ID': 'test-group',
    }
    with patch.dict(ENVIRONMENT_PATH, environment_variables), pytest.raises(ValidationError):
        # act
        BrokerKafkaConsumerSettings()


def test_consumer_settings_validate_session_pool_timeouts_valid() -> None:
    """Test session pool timeout validation with valid values."""
    # arrange
    broker_session_timeout_ms = 90000
    environment_variables = {
        'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092',
        'BROKER_TOPICS': 'TEST-TOPIC',
        'BROKER_GROUP_ID': 'test-group',
        'BROKER_MAX_POLL_INTERVAL_MS': str(broker_session_timeout_ms + 1),
        'BROKER_SESSION_TIMEOUT_MS': str(broker_session_timeout_ms),
    }
    with patch.dict(ENVIRONMENT_PATH, environment_variables):
        # act
        settings = BrokerKafkaConsumerSettings()

    # assert
    assert settings.max_poll_interval_ms == broker_session_timeout_ms + 1
    assert settings.session_timeout_ms == broker_session_timeout_ms


def test_consumer_settings_validate_session_pool_timeouts_invalid() -> None:
    """Test session pool timeout validation with invalid values."""
    # arrange
    broker_session_timeout_ms = 90000
    environment_variables = {
        'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092',
        'BROKER_TOPICS': 'TEST-TOPIC',
        'BROKER_GROUP_ID': 'test-group',
        'BROKER_MAX_POLL_INTERVAL_MS': str(broker_session_timeout_ms - 1),
        'BROKER_SESSION_TIMEOUT_MS': str(broker_session_timeout_ms),
    }
    with patch.dict(ENVIRONMENT_PATH, environment_variables), pytest.raises(ValidationError):
        # act
        BrokerKafkaConsumerSettings()


def test_consumer_settings_validate_session_heartbeat_valid() -> None:
    """Test session heartbeat validation with valid values."""
    # arrange
    heartbeat_interval_ms = 1000
    environment_variables = {
        'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092',
        'BROKER_TOPICS': 'TEST-TOPIC',
        'BROKER_GROUP_ID': 'test-group',
        'BROKER_SESSION_TIMEOUT_MS': str(5 * heartbeat_interval_ms),
        'BROKER_HEARTBEAT_INTERVAL_MS': str(heartbeat_interval_ms),
    }
    with patch.dict(ENVIRONMENT_PATH, environment_variables):
        # act
        settings = BrokerKafkaConsumerSettings()

    # assert
    assert settings.session_timeout_ms == 5 * heartbeat_interval_ms
    assert settings.heartbeat_interval_ms == heartbeat_interval_ms


def test_consumer_settings_validate_session_heartbeat_invalid() -> None:
    """Test session heartbeat validation with invalid values."""
    # arrange
    broker_heartbeat_interval_ms = 15000
    environment_variables = {
        'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092',
        'BROKER_TOPICS': 'TEST-TOPIC',
        'BROKER_GROUP_ID': 'test-group',
        'BROKER_SESSION_TIMEOUT_MS': str(broker_heartbeat_interval_ms),
        'BROKER_HEARTBEAT_INTERVAL_MS': str(broker_heartbeat_interval_ms),
    }
    with patch.dict(ENVIRONMENT_PATH, environment_variables), pytest.raises(ValidationError):
        # act
        BrokerKafkaConsumerSettings()


def test_producer_settings_create_with_valid_environment_variables() -> None:
    """Test creating producer settings with valid environment variables."""
    # arrange
    environment_variables = {'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092', 'BROKER_ACKS': 'all'}
    with patch.dict(ENVIRONMENT_PATH, environment_variables):
        # act
        settings = BrokerKafkaProducerSettings()

    # assert
    assert settings.bootstrap_servers == 'localhost:9092'
    assert settings.acks == BrokerKafkaAcks.ALL
    assert settings.connections_max_idle_ms == 10000


def test_producer_settings_create_with_custom_values() -> None:
    """Test creating producer settings with custom values."""
    # arrange
    environment_variables = {
        'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092',
        'BROKER_ACKS': '1',
        'BROKER_CONNECTIONS_MAX_IDLE_MS': '20000',
    }
    with patch.dict(ENVIRONMENT_PATH, environment_variables):
        # act
        settings = BrokerKafkaProducerSettings()

    # assert
    assert settings.bootstrap_servers == 'localhost:9092'
    assert settings.acks == BrokerKafkaAcks.ONE
    assert settings.connections_max_idle_ms == 20000


def test_producer_settings_create_with_defaults() -> None:
    """Test creating producer settings with default values."""
    # arrange
    environment_variables = {'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092'}
    with patch.dict(ENVIRONMENT_PATH, environment_variables):
        # act
        settings = BrokerKafkaProducerSettings()

    # assert
    assert settings.bootstrap_servers == 'localhost:9092'
    assert settings.acks == BrokerKafkaAcks.ALL
    assert settings.connections_max_idle_ms == 10000


@pytest.mark.parametrize(
    'acks_value,expected_result',
    [pytest.param('all', 'all', id='all'), pytest.param('1', 1, id='1'), pytest.param('0', 0, id='0')],
)
def test_producer_settings_parsed_acks(acks_value: str, expected_result: str | int) -> None:
    """Test parsed_acks method with different acks values."""
    # arrange
    environment_variables = {'BROKER_BOOTSTRAP_SERVERS': 'localhost:9092', 'BROKER_ACKS': acks_value}
    with patch.dict(ENVIRONMENT_PATH, environment_variables):
        settings = BrokerKafkaProducerSettings()

    # act
    result = settings.parsed_acks()

    # assert
    assert result == expected_result
