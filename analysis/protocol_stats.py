from collections import defaultdict
from .base_analyzer import BaseAnalyzer


class ProtocolStatsAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__()
        self.name = "ProtocolStatsAnalyzer"
        self.protocol_count = defaultdict(int)
        self.ip_communication = defaultdict(lambda: defaultdict(int))

    def analyze(self, packet):
        self.protocol_count[packet.protocol] += 1
        self.ip_communication[packet.src_ip][packet.dst_ip] += 1

    def finalize(self):
        self.results = {
            "protocol_distribution": dict(self.protocol_count),
            "top_communicating_pairs": sorted(
                [(src, dst, count) for src, targets in self.ip_communication.items()
                 for dst, count in targets.items()],
                key=lambda x: x[2],
                reverse=True
            )[:10]
        }

    def get_results(self):
        return self.results

    def reset(self):
        self.protocol_count.clear()
        self.ip_communication.clear()
        self.results = []