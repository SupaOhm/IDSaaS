"""
hybrid_detector.py — Hybrid NIDS Detector
Combines SignatureDetector (fast, rule-based) and LSTMDetector (learned anomaly).

Strategy:
  - Signature match alone can flag known attacks immediately.
  - LSTM flags unknown/zero-day anomalies the rules miss.
  - Combined score gives the full picture.
"""
from typing import Dict, Any, List

try:
    from .signature_detector import SignatureDetector
    from .lstm_detector import LSTMDetector
except ImportError:
    from signature_detector import SignatureDetector
    from lstm_detector import LSTMDetector


class HybridDetector:
    """
    Hybrid detector that fuses signature and LSTM results.

    Usage:
        detector = HybridDetector()
        result = detector.detect(event=event_dict, sequence=feature_list)

    The result includes both sub-detector outputs and a unified verdict.
    """

    def __init__(
        self,
        signature_detector: SignatureDetector = None,
        lstm_detector: LSTMDetector = None,
    ):
        self.sig = signature_detector or SignatureDetector()
        self.lstm = lstm_detector or LSTMDetector()

    def detect(self, event: Dict[str, Any], sequence: List = None) -> Dict[str, Any]:
        """
        Run both detectors and return a merged result dict.

        Args:
            event: raw event dict used by SignatureDetector.
            sequence: feature sequence used by LSTMDetector.

        Returns:
            {
                "alert": bool,          # True if either detector fires
                "signature": {...},     # raw SignatureDetector result
                "lstm_score": float,    # raw LSTM anomaly score
                "lstm_anomaly": bool,
            }
        """
        sig_result = self.sig.detect(event)
        lstm_score = self.lstm.detect(sequence or [])
        lstm_anomaly = self.lstm.is_anomaly(sequence or [])

        return {
            "alert": sig_result["matched"] or lstm_anomaly,
            "signature": sig_result,
            "lstm_score": lstm_score,
            "lstm_anomaly": lstm_anomaly,
        }

    def __repr__(self):
        return f"HybridDetector(sig={self.sig}, lstm={self.lstm})"
