from abc import ABC, abstractmethod


class BaseCapture(ABC):
    @abstractmethod
    def capture(self):
        """生成数据包的方法"""
        pass

    @abstractmethod
    def close(self):
        """释放资源"""
        pass