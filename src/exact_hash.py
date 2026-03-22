"""
exact_hash.py — Exact Hash Cache
In-memory lookup table for exact duplicate detection.
"""
import hashlib
import time
from collections import OrderedDict


class ExactHashCache:
    """
    Exact hash-based duplicate store.
    Optionally bounded by max_size (evicts oldest entries when full).
    TTL support is stubbed for future use.
    """

    def __init__(self, max_size: int = 50_000, ttl: float = None):
        self.max_size = max_size
        self.ttl = ttl  # placeholder — enforcement not yet implemented
        self._store: OrderedDict[str, float] = OrderedDict()

    def _hash(self, payload: str) -> str:
        return hashlib.sha256(payload.encode()).hexdigest()

    def add(self, payload: str) -> str:
        """Hash and store the payload. Returns the hash key."""
        key = self._hash(payload)
        if key in self._store:
            self._store.move_to_end(key)
        else:
            if len(self._store) >= self.max_size:
                self._store.popitem(last=False)  # evict oldest
            self._store[key] = time.monotonic()
        return key

    def contains(self, payload: str) -> bool:
        """Return True if an exact hash of this payload was previously added."""
        return self._hash(payload) in self._store

    def size(self) -> int:
        return len(self._store)

    def clear(self) -> None:
        self._store.clear()

    def __repr__(self):
        return f"ExactHashCache(max_size={self.max_size}, current_size={self.size()})"
