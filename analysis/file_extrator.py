import os
import re
from .base_analyzer import BaseAnalyzer


class FileExtractor(BaseAnalyzer):
    def __init__(self, output_dir='extracted_files'):
        super().__init__()
        self.output_dir = output_dir
        self.name = "FileExtractor"
        self.file_patterns = {
            'image': re.compile(b'\xFF\xD8\xFF\xE0\x00\x10JFIF'),  # JPEG
            'pdf': re.compile(b'%PDF-'),
            'exe': re.compile(b'MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00'),
            'zip': re.compile(b'PK\x03\x04'),
        }
        os.makedirs(output_dir, exist_ok=True)

    def analyze(self, packet):
        if packet.payload:
            for file_type, pattern in self.file_patterns.items():
                match = pattern.search(packet.payload)
                if match:
                    start_index = match.start()
                    self._extract_file(packet, file_type, start_index)

    def _extract_file(self, packet, file_type, start_index):
        """尝试从数据包中提取文件"""
        try:
            # 简单实现：从匹配位置到包尾
            file_data = packet.payload[start_index:]

            # 生成文件名
            filename = f"{packet.timestamp}_{packet.src_ip}_{file_type}.bin"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, 'wb') as f:
                f.write(file_data)

            self.results.append({
                'timestamp': packet.timestamp,
                'src_ip': packet.src_ip,
                'dst_ip': packet.dst_ip,
                'file_type': file_type,
                'filepath': filepath,
                'size': len(file_data)
            })
        except Exception as e:
            self.results.append({
                'error': f"提取文件失败: {str(e)}"
            })

    def finalize(self):
        # 对于文件提取，不需要特殊批处理
        pass

    def get_results(self):
        return self.results

    def reset(self):
        self.results = []