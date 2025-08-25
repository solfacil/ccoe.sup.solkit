import uuid
from contextvars import ContextVar

CORRELATION_ID_HEADER = 'X-Correlation-ID'
CORRELATION_ID_CONTEXT = 'trace_correlation_id'

trace_correlation_id_context: ContextVar[str | None] = ContextVar(CORRELATION_ID_CONTEXT, default=None)


def get_trace_correlation_id() -> str | None:
    """Get the correlation ID from the context."""
    return trace_correlation_id_context.get()


def set_trace_correlation_id(correlation_id: str) -> str:
    """Set the correlation ID in the context."""
    trace_correlation_id_context.set(correlation_id)
    return correlation_id


def create_trace_correlation_id() -> str:
    """Create a trace correlation ID for the current context."""
    correlation_id = str(uuid.uuid4())
    set_trace_correlation_id(correlation_id)
    return correlation_id
