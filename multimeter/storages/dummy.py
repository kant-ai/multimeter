"""Storage for measurement results"""
from .base import Storage


class DummyStorage(Storage):
    """Dummy Storage implementation"""

    def store(self, result):
        pass
