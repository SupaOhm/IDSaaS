"""
signature_detector.py — Rule-Based / Signature Detector
Simple rule-matching detector for known attack signatures.
Later this can be replaced with a live Snort integration.
"""
from typing import Dict, Any, List


# Placeholder rule set: {rule_name: callable(event) -> bool}
DEFAULT_RULES: Dict[str, Any] = {
    "port_scan": lambda e: e.get("dst_port_count", 0) > 20,
    "high_byte_rate": lambda e: e.get("bytes_per_sec", 0) > 1_000_000,
    "suspicious_protocol": lambda e: e.get("protocol", "").upper() in {"IRC", "TOR"},
}


class SignatureDetector:
    """
    Rule-based intrusion detector.

    Usage:
        detector = SignatureDetector()
        result = detector.detect(event_dict)
        # result: {"matched": bool, "rules_triggered": [...]}

    You can extend rules by calling:
        detector.add_rule("my_rule", lambda e: e.get("flag") == "BAD")

    Future: replace or augment with Snort/Suricata socket integration.
    """

    def __init__(self, rules: Optional[Dict] = None):
        self.rules: Dict[str, Any] = dict(DEFAULT_RULES)
        if rules:
            self.rules.update(rules)

    def add_rule(self, name: str, fn) -> None:
        self.rules[name] = fn

    def detect(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check an event dict against all loaded rules.
        Returns a result dict with matched flag and triggered rule names.
        """
        triggered: List[str] = []
        for name, fn in self.rules.items():
            try:
                if fn(event):
                    triggered.append(name)
            except Exception:
                pass  # malformed event field — skip rule
        return {"matched": bool(triggered), "rules_triggered": triggered}

    def __repr__(self):
        return f"SignatureDetector(rules={list(self.rules.keys())})"
