import asyncio
import time
from typing import Awaitable, Callable, Generic, TypeVar


T = TypeVar("T")


class AsyncTTLCache(Generic[T]):
    """單值非同步 TTL 快取，避免每次請求都打外部 API。"""

    def __init__(self, ttl_seconds: float):
        self._ttl = ttl_seconds
        self._value: T | None = None
        self._expires_at: float = 0.0
        self._lock = asyncio.Lock()

    async def get(self, fetch: Callable[[], Awaitable[T]]) -> T:
        async with self._lock:
            now = time.monotonic()
            if self._value is None or now >= self._expires_at:
                self._value = await fetch()
                self._expires_at = now + self._ttl
            return self._value

    def invalidate(self) -> None:
        self._value = None
        self._expires_at = 0.0
