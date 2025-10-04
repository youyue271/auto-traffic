import pyshark
from .base_capture import BaseCapture


class PysharkCapture(BaseCapture):
    def __init__(self, interface, filter=None):
        self.interface = interface
        self.filter = filter
        self.capture = pyshark.LiveCapture(
            interface=interface,
            display_filter=filter,
            use_json=True,
            include_raw=True
        )

    def capture(self):
        for packet in self.capture.sniff_continuously():
            yield packet

    def close(self):
        self.capture.close()