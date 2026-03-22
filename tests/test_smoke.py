"""
tests/test_smoke.py — Smoke tests for IDSaaS
Run with: pytest tests/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

def test_bloom_filter_basic():
    from bloom import BloomFilter
    bf = BloomFilter(capacity=1000, error_rate=0.01)
    bf.add("event_A")
    assert bf.contains("event_A") is True
    assert bf.contains("event_Z") is False

def test_exact_hash_basic():
    from exact_hash import ExactHashCache
    cache = ExactHashCache(max_size=10)
    assert cache.contains("hello") is False
    cache.add("hello")
    assert cache.contains("hello") is True

def test_dedup_engine_none():
    from dedup import DedupEngine
    engine = DedupEngine(strategy="none")
    assert engine.is_duplicate("anything") is False

def test_dedup_engine_exact():
    from dedup import DedupEngine
    engine = DedupEngine(strategy="exact")
    assert engine.is_duplicate("event_1") is False
    assert engine.is_duplicate("event_1") is True

def test_dedup_engine_bloom_exact():
    from dedup import DedupEngine
    engine = DedupEngine(strategy="bloom_exact")
    assert engine.is_duplicate("packet_x") is False
    assert engine.is_duplicate("packet_x") is True

def test_signature_detector():
    from signature_detector import SignatureDetector
    sig = SignatureDetector()
    result = sig.detect({"dst_port_count": 50, "bytes_per_sec": 0, "protocol": "TCP"})
    assert result["matched"] is True
    assert "port_scan" in result["rules_triggered"]

def test_lstm_detector_stub():
    from lstm_detector import LSTMDetector
    lstm = LSTMDetector(threshold=0.5)
    assert lstm.detect([]) == 0.0
    assert lstm.is_anomaly([]) is False

def test_hybrid_detector():
    from hybrid_detector import HybridDetector
    hybrid = HybridDetector()
    result = hybrid.detect(event={"dst_port_count": 50, "bytes_per_sec": 0, "protocol": "TCP"}, sequence=[])
    assert "alert" in result
    assert result["alert"] is True  # port_scan rule fires

def test_metrics():
    from metrics import classification_report
    y_true = [1, 0, 1, 1, 0]
    y_pred = [1, 0, 0, 1, 1]
    report = classification_report(y_true, y_pred)
    assert "f1" in report
    assert 0.0 <= report["f1"] <= 1.0
