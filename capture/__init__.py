from .pyshark_capture import PysharkCapture
from .scapy_capture import ScapyCapture


def get_capture_engine(engine_name, **kwargs):
    engines = {
        'pyshark': PysharkCapture,
        'scapy': ScapyCapture
    }
    if engine_name not in engines:
        raise ValueError(f"未知的抓包引擎: {engine_name}")
    return engines[engine_name](**kwargs)
