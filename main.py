"""
main.py — IDSaaS Experiment Runner

This is the central file for running experiments.
Change EXPERIMENT near the top to switch between modes.

Available experiments:
  "test_no_dedup"     — process all events without deduplication
  "test_exact_hash"   — deduplicate using ExactHashCache only
  "test_bloom_exact"  — deduplicate using BloomFilter + ExactHashCache
  "test_lstm_only"    — run LSTM detector (stub returns 0.0 until model loaded)
  "test_signature_only" — run rule-based signature detector
  "test_hybrid"       — run HybridDetector (signature + LSTM combined)
"""

import sys
import os

# ── Add src/ to path so you can run: python main.py ─────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from bloom import BloomFilter
from exact_hash import ExactHashCache
from dedup import DedupEngine
from lstm_detector import LSTMDetector
from signature_detector import SignatureDetector
from hybrid_detector import HybridDetector
from metrics import Timer, classification_report, print_report


# ─────────────────────────────────────────────────────────────────────────────
# CHANGE THIS to switch experiments
EXPERIMENT = "test_bloom_exact"
# ─────────────────────────────────────────────────────────────────────────────


# --- Synthetic Event Generator -----------------------------------------------
def make_events(n=1000, duplicate_ratio=0.3):
    """
    Generate synthetic network events as dicts.
    `duplicate_ratio` controls what fraction are exact duplicates.
    y_true labels: 0=normal, 1=attack (alternating pattern for demo).
    """
    import random, json
    events, labels = [], []
    base_events = [
        {"src_ip": f"10.0.0.{i}", "dst_port_count": random.randint(1, 50),
         "bytes_per_sec": random.randint(0, 2_000_000), "protocol": "TCP"}
        for i in range(int(n * (1 - duplicate_ratio)))
    ]
    for i in range(n):
        event = base_events[i % len(base_events)]
        events.append(event)
        labels.append(1 if i % 7 == 0 else 0)  # synthetic ground truth
    return events, labels


def event_str(e: dict) -> str:
    import json
    return json.dumps(e, sort_keys=True)


# --- Experiment Runners -------------------------------------------------------

def test_no_dedup(events, labels):
    timer = Timer()
    preds = []
    sig = SignatureDetector()
    timer.start()
    for e in events:
        r = sig.detect(e)
        preds.append(1 if r["matched"] else 0)
    timer.stop()
    print_report("No Dedup + Signature", classification_report(labels, preds), timer.summary(len(events)))


def test_exact_hash(events, labels):
    dedup = DedupEngine(strategy="exact")
    timer = Timer()
    sig = SignatureDetector()
    preds, seen = [], 0
    timer.start()
    for e, lbl in zip(events, labels):
        if dedup.is_duplicate(event_str(e)):
            preds.append(0)  # skipped = assume normal
            continue
        seen += 1
        r = sig.detect(e)
        preds.append(1 if r["matched"] else 0)
    timer.stop()
    print(f"  [ExactHash] Processed {seen}/{len(events)} unique events. Dedup stats: {dedup.stats()}")
    print_report("Exact Hash Dedup + Signature", classification_report(labels, preds), timer.summary(len(events)))


def test_bloom_exact(events, labels):
    dedup = DedupEngine(strategy="bloom_exact")
    timer = Timer()
    sig = SignatureDetector()
    preds, seen = [], 0
    timer.start()
    for e, lbl in zip(events, labels):
        if dedup.is_duplicate(event_str(e)):
            preds.append(0)
            continue
        seen += 1
        r = sig.detect(e)
        preds.append(1 if r["matched"] else 0)
    timer.stop()
    print(f"  [BloomExact] Processed {seen}/{len(events)} unique events. Dedup stats: {dedup.stats()}")
    print_report("Bloom+Exact Dedup + Signature", classification_report(labels, preds), timer.summary(len(events)))


def test_lstm_only(events, labels):
    lstm = LSTMDetector(threshold=0.5)
    timer = Timer()
    preds = []
    timer.start()
    for e in events:
        score = lstm.detect([])  # placeholder — no real features yet
        preds.append(1 if lstm.is_anomaly([]) else 0)
    timer.stop()
    print_report("LSTM Only (stub)", classification_report(labels, preds), timer.summary(len(events)))


def test_signature_only(events, labels):
    sig = SignatureDetector()
    timer = Timer()
    preds = []
    timer.start()
    for e in events:
        r = sig.detect(e)
        preds.append(1 if r["matched"] else 0)
    timer.stop()
    print_report("Signature Only", classification_report(labels, preds), timer.summary(len(events)))


def test_hybrid(events, labels):
    hybrid = HybridDetector()
    timer = Timer()
    preds = []
    timer.start()
    for e in events:
        r = hybrid.detect(event=e, sequence=[])
        preds.append(1 if r["alert"] else 0)
    timer.stop()
    print_report("Hybrid (Signature + LSTM stub)", classification_report(labels, preds), timer.summary(len(events)))


# --- Dispatch ----------------------------------------------------------------

EXPERIMENTS = {
    "test_no_dedup": test_no_dedup,
    "test_exact_hash": test_exact_hash,
    "test_bloom_exact": test_bloom_exact,
    "test_lstm_only": test_lstm_only,
    "test_signature_only": test_signature_only,
    "test_hybrid": test_hybrid,
}

if __name__ == "__main__":
    print(f"\n[IDSaaS] Running experiment: {EXPERIMENT}")
    events, labels = make_events(n=2000, duplicate_ratio=0.35)
    fn = EXPERIMENTS.get(EXPERIMENT)
    if fn is None:
        print(f"Unknown experiment: {EXPERIMENT!r}. Choose from: {list(EXPERIMENTS)}")
        sys.exit(1)
    fn(events, labels)
