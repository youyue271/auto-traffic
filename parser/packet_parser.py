from .unified_format import UnifiedPacket


class PacketParser:
    def parse(self, raw_packet):
        """将原始数据包解析为统一格式"""
        packet = UnifiedPacket()

        # 根据不同引擎解析
        if hasattr(raw_packet, 'sniff_time'):  # Pyshark
            packet.timestamp = raw_packet.sniff_time.timestamp()
            packet.src_ip = getattr(raw_packet, 'ip', None).src if hasattr(raw_packet, 'ip') else None
            packet.dst_ip = getattr(raw_packet, 'ip', None).dst if hasattr(raw_packet, 'ip') else None
            packet.src_port = getattr(raw_packet, getattr(raw_packet, 'transport_layer', None),
                                      None).srcport if hasattr(raw_packet, 'transport_layer') else None
            packet.dst_port = getattr(raw_packet, getattr(raw_packet, 'transport_layer', None),
                                      None).dstport if hasattr(raw_packet, 'transport_layer') else None
            packet.protocol = raw_packet.highest_layer
            packet.payload = raw_packet.get_raw_packet() if hasattr(raw_packet, 'get_raw_packet') else None

            # 元数据提取
            packet.metadata = self._extract_metadata(raw_packet)

        else:  # Scapy
            packet.timestamp = raw_packet.time
            packet.src_ip = raw_packet.getlayer('IP').src if raw_packet.haslayer('IP') else None
            packet.dst_ip = raw_packet.getlayer('IP').dst if raw_packet.haslayer('IP') else None
            packet.src_port = raw_packet.getlayer('TCP').sport if raw_packet.haslayer('TCP') else None
            packet.dst_port = raw_packet.getlayer('TCP').dport if raw_packet.haslayer('TCP') else None
            packet.protocol = raw_packet.lastlayer().name
            packet.payload = bytes(raw_packet.payload) if raw_packet.payload else None
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
                'user_agent': getattr(http_layer, 'user_agent', None)
            }

        # DNS协议元数据
        if hasattr(raw_packet, 'dns'):
            dns_layer = raw_packet.dns
            metadata['dns'] = {
                'query': getattr(dns_layer, 'qry_name', None),
                'type': getattr(dns_layer, 'qry_type', None)
            }

        # 添加其他协议解析...
        return metadata