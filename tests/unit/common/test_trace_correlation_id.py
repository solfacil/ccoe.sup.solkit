import uuid
from contextvars import Context
from unittest.mock import patch

from solkit.common.trace_correlation_id import (
    create_trace_correlation_id,
    get_trace_correlation_id,
    set_trace_correlation_id,
    trace_correlation_id_context,
    # CORRELATION_ID_HEADER,
    # CORRELATION_ID_CONTEXT,
)


def test_trace_correlation_id_get_then_return_none() -> None:
    """Test the get correlation id method."""
    # arrange
    context = Context()
    # act
    result = context.run(get_trace_correlation_id)
    # assert
    assert context.run(lambda: trace_correlation_id_context.get()) is None
    assert result is None


def test_trace_correlation_id_get_then_return_correlation_id() -> None:
    """Test the get correlation id method."""
    # arrange
    correlation_id = str(uuid.uuid4())
    context = Context()
    context.run(lambda: trace_correlation_id_context.set(correlation_id))
    # act
    result = context.run(lambda: get_trace_correlation_id())
    # assert
    assert context.run(lambda: trace_correlation_id_context.get()) == correlation_id
    assert result == correlation_id


def test_trace_correlation_id_set_then_return_correlation_id() -> None:
    """Test the set correlation id method."""
    # arrange
    correlation_id = str(uuid.uuid4())
    context = Context()
    # act
    result = context.run(lambda: set_trace_correlation_id(correlation_id))
    # assert
    assert context.run(lambda: trace_correlation_id_context.get()) == correlation_id
    assert result == correlation_id


def test_trace_correlation_id_create_then_return_correlation_id() -> None:
    """Test the create correlation id method."""
    # arrange
    correlation_id = uuid.uuid4()
    context = Context()
    with patch('uuid.uuid4', return_value=correlation_id):
        # act
        result = context.run(create_trace_correlation_id)

    # assert
    assert context.run(lambda: trace_correlation_id_context.get()) == str(correlation_id)
    assert result == str(correlation_id)
