class UnifiedPacket:
    def __init__(self):
        self.timestamp = None
        self.src_ip = None
        self.dst_ip = None
        self.src_port = None
        self.dst_port = None
        self.protocol = None
        self.payload = None
        self.metadata = {}  # 协议特定元数据

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "src": f"{self.src_ip}:{self.src_port}",
            "dst": f"{self.dst_ip}:{self.dst_port}",
            "protocol": self.protocol,
            "payload_size": len(self.payload) if self.payload else 0,
            "metadata": self.metadata
        }