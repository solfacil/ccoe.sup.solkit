from unittest.mock import Mock

import pytest
from aiokafka.structs import ConsumerRecord
from freezegun import freeze_time

from solkit.broker.abstracts import BrokerAdapterAbstract
from solkit.broker.repository import BrokerRepository
from solkit.common.trace_correlation_id import CORRELATION_ID_HEADER


@pytest.mark.parametrize(
    'key, expected',
    [
        pytest.param('test', b'test', id='key-as-string'),
        pytest.param(b'test', b'test', id='key-as-bytes'),
    ],
)
def test_broker_repository_parse_message_key_then_return_bytes(key: str | bytes, expected: bytes) -> None:
    """Test the parse message key method."""
    # arrange
    # act
    result = BrokerRepository._parse_message_key(key)
    # assert
    assert result == expected


def test_broker_repository_parse_message_value_then_return_bytes() -> None:
    """Test the parse message value method."""
    # arrange
    value = {'some': 'data'}
    metadata = {'some': 'metadata'}
    # act
    result = BrokerRepository._parse_message_value(value, metadata)
    # assert
    assert result == b'{"data": {"some": "data"}, "metadata": {"some": "metadata"}}'


def test_broker_repository_unparse_message_value_then_return_tuple() -> None:
    """Test the unparse message value method."""
    # arrange
    message = b'{"data": {"some": "data"}, "metadata": {"some": "metadata"}}'
    # act
    result = BrokerRepository._unparse_message_value(message)
    # assert
    assert result[0] == {'some': 'data'}
    assert result[1] == {'some': 'metadata'}


def test_broker_repository_set_correlation_id_then_return_list() -> None:
    """Test the set correlation id method."""
    # arrange
    # act
    result = BrokerRepository._set_correlation_id()
    # assert
    assert result == []


def test_broker_repository_get_correlation_id_then_return_none() -> None:
    """Test the get correlation id method."""
    # arrange
    message = Mock(spec=ConsumerRecord)
    message.headers = []
    # act
    result = BrokerRepository._get_correlation_id(message)
    # assert
    assert result is None


def test_broker_repository_get_correlation_id_then_return_correlation_id() -> None:
    """Test the get correlation id method."""
    # arrange
    message = Mock(spec=ConsumerRecord)
    message.headers = [(CORRELATION_ID_HEADER, b'test-correlation-id')]
    # act
    result = BrokerRepository._get_correlation_id(message)
    # assert
    assert result == 'test-correlation-id'


@pytest.mark.parametrize(
    'topic, retry_max_times, expected',
    [
        pytest.param('TOPIC', 3, 'TOPIC-RETRY-1', id='without-retry-suffix'),
        pytest.param('TOPIC-RETRY-1', 3, 'TOPIC-RETRY-2', id='with-retry-suffix'),
        pytest.param('TOPIC-RETRY-3', 3, 'TOPIC-DLQ', id='with-retry-suffix-and-max-retries'),
        pytest.param('TOPIC-DLQ', 3, None, id='with-dlq-suffix'),
    ],
)
def test_broker_repository_next_retry_topic_then_return_str_or_none(
    topic: str,
    retry_max_times: int,
    expected: str | None,
) -> None:
    """Test the next retry topic method."""
    # arrange
    # act
    result = BrokerRepository._next_retry_topic(topic, retry_max_times)
    # assert
    assert result == expected


@freeze_time('2025-08-13T12:00:00.000000Z')
def test_broker_repository_concat_metadata_then_return_dict() -> None:
    """Test the concat metadata method."""
    # arrange
    topic = 'SOME-TOPIC'
    metadata = {'extra': 'metadata'}
    common_metadata = {'common': 'metadata'}
    broker_mock = Mock(spec=BrokerAdapterAbstract)
    repository = BrokerRepository(adapter=broker_mock, metadata=common_metadata)
    # act
    result = repository._concat_metadata(topic, metadata)
    # assert
    assert result[topic.lower()] == '2025-08-13T12:00:00+00:00'
    assert result['common'] == 'metadata'
    assert result['extra'] == 'metadata'
