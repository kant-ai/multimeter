"""Base class Storage for measurement results"""
import abc


# pylint: disable=too-few-public-methods
class Storage(abc.ABC):
    """
    Base class for implementing storages, which store the results of measurements.
    """

    @abc.abstractmethod
    def store(self, result):
        """
        Store the result.

        Args:
            result (multimeter.result.Result): The result to be stored.
        """
