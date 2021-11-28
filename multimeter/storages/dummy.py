"""Storage for measurement results"""
from .base import Storage


# pylint: disable=too-few-public-methods
class DummyStorage(Storage):
    """Dummy Storage implementation"""

    def store(self, result):
        pass
