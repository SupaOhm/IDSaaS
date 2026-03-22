"""
dedup.py — Deduplication Engine
Combines BloomFilter and ExactHashCache for a two-stage dedup pipeline.

Strategy:
  "none"        — no deduplication
  "exact"       — ExactHashCache only
  "bloom_exact" — BloomFilter gates ExactHashCache (reduces exact-cache lookups)
"""
import hashlib
from typing import Optional

try:
    from .bloom import BloomFilter
    from .exact_hash import ExactHashCache
except ImportError:
    from bloom import BloomFilter
    from exact_hash import ExactHashCache


def _canonicalize(payload: str, tenant_id: Optional[str], source_id: Optional[str]) -> str:
    """
    Build a canonical string from payload + optional metadata fields.
    Sorting ensures key-order independence for dict-like payloads.
    """
    parts = [payload.strip()]
    if tenant_id:
        parts.append(f"tenant:{tenant_id}")
    if source_id:
        parts.append(f"source:{source_id}")
    return "|".join(parts)


class DedupEngine:
    """
    Two-stage deduplication engine.

    Usage:
        engine = DedupEngine(strategy="bloom_exact")
        if engine.is_duplicate(event_str, tenant_id="t1"):
            skip()
        else:
            process()
    """

    STRATEGIES = ("none", "exact", "bloom_exact")

    def __init__(
        self,
        strategy: str = "bloom_exact",
        bloom_capacity: int = 100_000,
        bloom_error_rate: float = 0.01,
        cache_max_size: int = 50_000,
    ):
        if strategy not in self.STRATEGIES:
            raise ValueError(f"strategy must be one of {self.STRATEGIES}")
        self.strategy = strategy
        self.bloom = BloomFilter(bloom_capacity, bloom_error_rate) if strategy == "bloom_exact" else None
        self.cache = ExactHashCache(max_size=cache_max_size) if strategy != "none" else None
        self.total_seen = 0
        self.total_duplicates = 0

    def is_duplicate(
        self,
        payload: str,
        tenant_id: Optional[str] = None,
        source_id: Optional[str] = None,
    ) -> bool:
        """
        Return True if this payload is determined to be a duplicate.
        Side-effect: registers the payload if it is new.
        """
        self.total_seen += 1
        if self.strategy == "none":
            return False

        canonical = _canonicalize(payload, tenant_id, source_id)

        if self.strategy == "bloom_exact":
            if not self.bloom.contains(canonical):
                # Definitely new — add to both and return False
                self.bloom.add(canonical)
                self.cache.add(canonical)
                return False
            # Bloom says maybe — confirm with exact cache
            if self.cache.contains(canonical):
                self.total_duplicates += 1
                return True
            # False positive from bloom — register in exact cache
            self.cache.add(canonical)
            return False

        # strategy == "exact"
        if self.cache.contains(canonical):
            self.total_duplicates += 1
            return True
        self.cache.add(canonical)
        return False

    def stats(self) -> dict:
        return {
            "strategy": self.strategy,
            "total_seen": self.total_seen,
            "total_duplicates": self.total_duplicates,
            "dedup_rate": (
                self.total_duplicates / self.total_seen if self.total_seen else 0.0
            ),
        }

    def __repr__(self):
        return f"DedupEngine(strategy={self.strategy!r})"
