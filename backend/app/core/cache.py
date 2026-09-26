import time
from typing import Any


class TTLCache:

    def __init__(self):
        self._cache: dict[str, tuple[Any, float]] = {}

    def set(
        self,
        key: str,
        value: Any,
        ttl: int = 300,
    ) -> None:
        expires_at = time.time() + ttl
        self._cache[key] = (value, expires_at)

    def get(self, key: str) -> Any | None:
        item = self._cache.get(key)

        if item is None:
            return None

        value, expires_at = item

        if time.time() >= expires_at:
            self.delete(key)
            return None

        return value

    def delete(self, key: str) -> None:
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()


cache = TTLCache()