"""Base class Storage for measurement results"""
import abc


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
