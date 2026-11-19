"""Lightweight in-memory cache with TTL and telemetry for UdyamSathi."""

import time
from typing import Any


class SimpleCache:
    def __init__(self, maxsize: int = 1000, default_ttl: float = 300.0) -> None:
        self.maxsize = maxsize
        self.default_ttl = default_ttl
        self._store: dict[str, tuple[float, Any]] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Any | None:
        now = time.time()
        item = self._store.get(key)
        if item is None:
            self.misses += 1
            return None
        expires_at, value = item
        if now > expires_at:
            del self._store[key]
            self.misses += 1
            return None
        self.hits += 1
        return value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        if len(self._store) >= self.maxsize:
            # Drop oldest 20%
            oldest_keys = sorted(
                self._store.keys(), key=lambda k: self._store[k][0]
            )[: max(1, self.maxsize // 5)]
            for k in oldest_keys:
                self._store.pop(k, None)
        duration = ttl if ttl is not None else self.default_ttl
        self._store[key] = (time.time() + duration, value)

    def stats(self) -> dict[str, Any]:
        total = self.hits + self.misses
        hit_rate = (self.hits / total) if total > 0 else 0.0
        return {
            "size": len(self._store),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 4),
        }

    def clear(self) -> None:
        self._store.clear()
        self.hits = 0
        self.misses = 0


query_cache = SimpleCache()
