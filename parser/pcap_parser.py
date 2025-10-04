import pyshark
from .unified_format import UnifiedPacket


class PcapParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.capture = pyshark.FileCapture(
            filepath,
            use_json=True,
            include_raw=True,
            keep_packets=False  # 节省内存
        )

    def parse(self):
        """解析PCAP文件并生成统一格式的数据包"""
        for packet in self.capture:
            yield self._parse_packet(packet)

    def _parse_packet(self, raw_packet):
        """将原始数据包解析为统一格式"""
        packet = UnifiedPacket()
        packet.timestamp = raw_packet.sniff_time.timestamp()

        # IP层信息
        if hasattr(raw_packet, 'ip'):
            packet.src_ip = raw_packet.ip.src
            packet.dst_ip = raw_packet.ip.dst

        # 传输层信息
        if hasattr(raw_packet, 'tcp'):
            packet.src_port = raw_packet.tcp.srcport
            packet.dst_port = raw_packet.tcp.dstport
            packet.protocol = 'TCP'
        elif hasattr(raw_packet, 'udp'):
            packet.src_port = raw_packet.udp.srcport
            packet.dst_port = raw_packet.udp.dstport
            packet.protocol = 'UDP'
        else:
            packet.protocol = raw_packet.highest_layer

        # 负载数据
        if hasattr(raw_packet, 'get_raw_packet'):
            packet.payload = raw_packet.get_raw_packet()

        # 元数据提取
        packet.metadata = self._extract_metadata(raw_packet)

        return packet

    def _extract_metadata(self, raw_packet):
        """提取协议特定元数据"""
        metadata = {}

        # HTTP协议元数据
        if hasattr(raw_packet, 'http'):
            http_layer = raw_packet.http
            metadata['http'] = {
                'method': getattr(http_layer, 'request_method', None),
                'uri': getattr(http_layer, 'request_uri', None),
                'host': getattr(http_layer, 'host', None),
                'user_agent': getattr(http_layer, 'user_agent', None),
                'content_type': getattr(http_layer, 'content_type', None)
            }

        # DNS协议元数据
        if hasattr(raw_packet, 'dns'):
            dns_layer = raw_packet.dns
            metadata['dns'] = {
                'query': getattr(dns_layer, 'qry_name', None),
                'type': getattr(dns_layer, 'qry_type', None),
                'response': getattr(dns_layer, 'resp_name', None)
            }

        # TLS/SSL元数据
        if hasattr(raw_packet, 'ssl'):
            ssl_layer = raw_packet.ssl
            metadata['ssl'] = {
                'version': getattr(ssl_layer, 'record_version', None),
                'cipher': getattr(ssl_layer, 'cipher', None),
                'server_name': getattr(ssl_layer, 'handshake_extensions_server_name', None)
            }

        return metadata
