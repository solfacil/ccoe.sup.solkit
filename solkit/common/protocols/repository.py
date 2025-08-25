from typing import Protocol, runtime_checkable


@runtime_checkable
class BaseRepositoryProtocol(Protocol):
    """Base repository protocol."""

    async def healthcheck(self) -> tuple[bool, str | None]:
        """Healthcheck the repository."""
        ...
