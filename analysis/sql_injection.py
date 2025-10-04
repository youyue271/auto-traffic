import re
from .base_analyzer import BaseAnalyzer


class SQLInjectionAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__()
        self.name = "SQLInjectionAnalyzer"
        self.patterns = [
            re.compile(r"SELECT.*FROM", re.IGNORECASE),
            re.compile(r"UNION.*SELECT", re.IGNORECASE),
            re.compile(r"1=1", re.IGNORECASE),
            re.compile(r"SLEEP\(\d+\)", re.IGNORECASE)
        ]
        self.suspicious_packets = []

    def analyze(self, packet):
        if packet.protocol == "HTTP" and packet.payload:
            payload = packet.payload.decode('utf-8', errors='ignore')
            for pattern in self.patterns:
                if pattern.search(payload):
                    self.suspicious_packets.append({
                        "timestamp": packet.timestamp,
                        "src": packet.src_ip,
                        "dst": packet.dst_ip,
                        "matched_pattern": pattern.pattern,
                        "payload_snippet": payload[:200] + "..." if len(payload) > 200 else payload
                    })
                    break

    def finalize(self):
        self.results = {
            "total_detections": len(self.suspicious_packets),
            "detections": self.suspicious_packets
        }

    def get_results(self):
        return self.results

    def reset(self):
        self.suspicious_packets = []
        self.results = []