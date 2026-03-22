"""
utils.py — Shared Utilities
Keep this file lean. Only add helpers that are clearly shared across modules.
"""
import json
import hashlib
from typing import Any


def hash_payload(payload: str) -> str:
    """SHA-256 fingerprint of an event payload string."""
    return hashlib.sha256(payload.encode()).hexdigest()


def event_to_str(event: Any) -> str:
    """Serialize an event dict/object to a canonical JSON string."""
    if isinstance(event, dict):
        return json.dumps(event, sort_keys=True)
    return str(event)


def load_csv_events(path: str):
    """
    Lazy generator yielding rows from a CSV as dicts.
    Use for streaming large datasets without loading all into memory.
    """
    import csv
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row
