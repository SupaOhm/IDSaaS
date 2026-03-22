"""
IDSaaS — Intrusion Detection System as a Service
Flat, modular research prototype. Import anything from src/.
"""

from .bloom import BloomFilter
from .exact_hash import ExactHashCache
from .dedup import DedupEngine
from .lstm_detector import LSTMDetector
from .signature_detector import SignatureDetector
from .hybrid_detector import HybridDetector
from .metrics import classification_report, Timer, print_report
