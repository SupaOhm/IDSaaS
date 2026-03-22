"""
bloom.py — Bloom Filter
A simple, in-memory Bloom filter for probabilistic duplicate detection.
"""
import hashlib
import math


class BloomFilter:
    """
    Probabilistic set membership structure.
    Fast and memory-efficient, but may produce false positives (never false negatives).
    """

    def __init__(self, capacity: int = 100_000, error_rate: float = 0.01):
        self.capacity = capacity
        self.error_rate = error_rate
        self.bit_count = self._optimal_bit_count(capacity, error_rate)
        self.hash_count = self._optimal_hash_count(self.bit_count, capacity)
        self.bit_array = bytearray(math.ceil(self.bit_count / 8))
        self.num_added = 0

    def _optimal_bit_count(self, n: int, p: float) -> int:
        return int(-n * math.log(p) / (math.log(2) ** 2))

    def _optimal_hash_count(self, m: int, n: int) -> int:
        return max(1, int((m / n) * math.log(2)))

    def _hashes(self, item: str):
        """Generate k hash positions for the given item."""
        h1 = int(hashlib.md5(item.encode()).hexdigest(), 16)
        h2 = int(hashlib.sha256(item.encode()).hexdigest(), 16)
        for i in range(self.hash_count):
            yield (h1 + i * h2) % self.bit_count

    def add(self, item: str) -> None:
        """Add an item to the filter."""
        for pos in self._hashes(item):
            byte_idx, bit_idx = divmod(pos, 8)
            self.bit_array[byte_idx] |= (1 << bit_idx)
        self.num_added += 1

    def contains(self, item: str) -> bool:
        """Return True if the item is probably in the set."""
        return all(
            self.bit_array[byte_idx] & (1 << bit_idx)
            for pos in self._hashes(item)
            for byte_idx, bit_idx in [divmod(pos, 8)]
        )

    def __repr__(self):
        return (
            f"BloomFilter(capacity={self.capacity}, error_rate={self.error_rate}, "
            f"added={self.num_added}, bits={self.bit_count})"
        )
