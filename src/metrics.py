"""
metrics.py — Detection & System Evaluation Helpers
Simple functions for computing detection effectiveness and system efficiency.
"""
from typing import List, Dict
import time


# ── Detection Effectiveness ──────────────────────────────────────────────────

def accuracy(y_true: List[int], y_pred: List[int]) -> float:
    assert len(y_true) == len(y_pred), "Length mismatch"
    return sum(t == p for t, p in zip(y_true, y_pred)) / len(y_true)


def precision(y_true: List[int], y_pred: List[int]) -> float:
    tp = sum(t == 1 and p == 1 for t, p in zip(y_true, y_pred))
    fp = sum(t == 0 and p == 1 for t, p in zip(y_true, y_pred))
    return tp / (tp + fp) if (tp + fp) else 0.0


def recall(y_true: List[int], y_pred: List[int]) -> float:
    tp = sum(t == 1 and p == 1 for t, p in zip(y_true, y_pred))
    fn = sum(t == 1 and p == 0 for t, p in zip(y_true, y_pred))
    return tp / (tp + fn) if (tp + fn) else 0.0


def f1_score(y_true: List[int], y_pred: List[int]) -> float:
    p = precision(y_true, y_pred)
    r = recall(y_true, y_pred)
    return 2 * p * r / (p + r) if (p + r) else 0.0


def false_alarm_rate(y_true: List[int], y_pred: List[int]) -> float:
    """FAR = FP / (FP + TN)"""
    fp = sum(t == 0 and p == 1 for t, p in zip(y_true, y_pred))
    tn = sum(t == 0 and p == 0 for t, p in zip(y_true, y_pred))
    return fp / (fp + tn) if (fp + tn) else 0.0


def classification_report(y_true: List[int], y_pred: List[int]) -> Dict[str, float]:
    return {
        "accuracy": accuracy(y_true, y_pred),
        "precision": precision(y_true, y_pred),
        "recall": recall(y_true, y_pred),
        "f1": f1_score(y_true, y_pred),
        "far": false_alarm_rate(y_true, y_pred),
    }


# ── System Efficiency ─────────────────────────────────────────────────────────

class Timer:
    """Simple wall-clock timer for latency/throughput measurement."""

    def __init__(self):
        self._start = None
        self._elapsed: List[float] = []

    def start(self):
        self._start = time.perf_counter()

    def stop(self) -> float:
        elapsed = time.perf_counter() - self._start
        self._elapsed.append(elapsed)
        return elapsed

    def throughput(self, n_events: int) -> float:
        """Events per second over all recorded intervals."""
        total = sum(self._elapsed)
        return n_events / total if total > 0 else 0.0

    def avg_latency_ms(self) -> float:
        if not self._elapsed:
            return 0.0
        return (sum(self._elapsed) / len(self._elapsed)) * 1000

    def summary(self, n_events: int) -> Dict[str, float]:
        return {
            "total_time_s": round(sum(self._elapsed), 4),
            "avg_latency_ms": round(self.avg_latency_ms(), 4),
            "throughput_eps": round(self.throughput(n_events), 2),
        }


def print_report(label: str, det_metrics: Dict, sys_metrics: Dict = None) -> None:
    print(f"\n{'=' * 50}")
    print(f"  {label}")
    print(f"{'=' * 50}")
    for k, v in det_metrics.items():
        print(f"  {k:<20} {v:.4f}")
    if sys_metrics:
        print(f"  {'---'}")
        for k, v in sys_metrics.items():
            print(f"  {k:<20} {v}")
    print()
