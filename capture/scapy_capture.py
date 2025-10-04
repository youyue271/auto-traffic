from scapy.all import sniff
from .base_capture import BaseCapture


class ScapyCapture(BaseCapture):
    def __init__(self, interface, filter=None):
        self.interface = interface
        self.filter = filter
        self.running = True

    def capture(self):
        for packet in sniff(iface=self.interface, filter=self.filter, store=False):
            if not self.running:
                break
            yield packet

    def close(self):
        self.running = False