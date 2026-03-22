"""
main.py — IDSaaS Experiment Runner

Configure your pipeline using the toggles below.
The pipeline assembles itself from whatever you enable.

─────────────────────────────────────────────
 PIPELINE CONFIGURATION  ← edit here
─────────────────────────────────────────────
"""

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from bloom import BloomFilter
from exact_hash import ExactHashCache
from dedup import DedupEngine
from lstm_detector import LSTMDetector
from signature_detector import SignatureDetector
from hybrid_detector import HybridDetector
from metrics import classification_report, Timer, print_report

# ── Toggle components on/off ──────────────────────────────────────────────────
USE_BLOOM      = True   # Bloom filter pre-check before exact cache
USE_EXACT_HASH = True   # Exact hash cache deduplication
USE_SIGNATURE  = True   # Rule-based signature detection
USE_LSTM       = False  # LSTM anomaly detection (stub until model is trained)

# ── Tuning parameters ─────────────────────────────────────────────────────────
BLOOM_CAPACITY    = 100_000
BLOOM_ERROR_RATE  = 0.01
CACHE_MAX_SIZE    = 50_000
LSTM_THRESHOLD    = 0.5
N_EVENTS          = 2000
DUPLICATE_RATIO   = 0.35
# ─────────────────────────────────────────────────────────────────────────────


def build_pipeline():
    """Assemble the pipeline from the toggles above."""

    # Dedup strategy
    if USE_BLOOM and USE_EXACT_HASH:
        dedup_strategy = "bloom_exact"
    elif USE_EXACT_HASH:
        dedup_strategy = "exact"
    else:
        dedup_strategy = "none"

    dedup = DedupEngine(
        strategy=dedup_strategy,
        bloom_capacity=BLOOM_CAPACITY,
        bloom_error_rate=BLOOM_ERROR_RATE,
        cache_max_size=CACHE_MAX_SIZE,
    )

    # Detectors
    sig  = SignatureDetector() if USE_SIGNATURE else None
    lstm = LSTMDetector(threshold=LSTM_THRESHOLD) if USE_LSTM else None

    label = (
        f"{'Bloom+' if USE_BLOOM else ''}"
        f"{'ExactHash+' if USE_EXACT_HASH else ''}"
        f"{'Signature+' if USE_SIGNATURE else ''}"
        f"{'LSTM' if USE_LSTM else ''}"
    ).strip("+") or "No components"

    return dedup, sig, lstm, label


def make_events(n=1000, duplicate_ratio=0.3):
    import random
    base = [
        {
            "src_ip": f"10.0.0.{i % 255}",
            "dst_port_count": random.randint(1, 50),
            "bytes_per_sec": random.randint(0, 2_000_000),
            "protocol": random.choice(["TCP", "UDP", "IRC"]),
        }
        for i in range(int(n * (1 - duplicate_ratio)))
    ]
    events, labels = [], []
    for i in range(n):
        events.append(base[i % len(base)])
        labels.append(1 if i % 7 == 0 else 0)
    return events, labels


def run(events, labels, dedup, sig, lstm):
    timer = Timer()
    preds = []
    timer.start()

    for event in events:
        payload = json.dumps(event, sort_keys=True)

        # Dedup stage
        if dedup.is_duplicate(payload):
            preds.append(0)  # skipped — treated as normal
            continue

        alert = False

        # Signature stage
        if sig:
            result = sig.detect(event)
            alert = alert or result["matched"]

        # LSTM stage
        if lstm:
            alert = alert or lstm.is_anomaly([])  # pass real features here later

        preds.append(1 if alert else 0)

    timer.stop()
    return preds, timer


if __name__ == "__main__":
    dedup, sig, lstm, label = build_pipeline()

    print(f"\n[IDSaaS] Pipeline: {label}")
    print(f"  bloom={USE_BLOOM}  exact_hash={USE_EXACT_HASH}  "
          f"signature={USE_SIGNATURE}  lstm={USE_LSTM}\n")

    events, labels = make_events(n=N_EVENTS, duplicate_ratio=DUPLICATE_RATIO)
    preds, timer = run(events, labels, dedup, sig, lstm)

    det = classification_report(labels, preds)
    sys._metrics = timer.summary(len(events))
    print_report(label, det, timer.summary(len(events)))
    print(f"  Dedup stats: {dedup.stats()}\n")
