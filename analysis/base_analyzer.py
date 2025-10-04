from abc import ABC, abstractmethod

from parser.unified_format import UnifiedPacket


class BaseAnalyzer(ABC):
    def __init__(self):
        self.results = []
        self.name = ""

    @abstractmethod
    def analyze(self, packet: UnifiedPacket):
        """处理单个数据包"""
        pass

    @abstractmethod
    def finalize(self):
        """批次处理完成后调用"""
        pass

    @abstractmethod
    def get_results(self):
        """返回分析结果"""
        pass

    @abstractmethod
    def reset(self):
        """重置分析器状态"""
        pass