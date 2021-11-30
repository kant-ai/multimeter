"""The module defining the Multimeter class"""
from multimeter.measurement import Measurement
from multimeter.storages.dummy import DummyStorage


class Multimeter:
    """
    A `Multimeter` object allows to measure run-time properties of python code.

    The multi meter uses `multimeter.probe.Probe` objects that are used for actually
    measuring some metrics on individual subjects. Those probes are defined, when a
    new instance of `Multimeter` is created.

    A new series of measurement is created when the method `measure()` is being called.
    The measuring process itself is started by calling `start()` and runs until it is
    ended by calling `end()`. The measuring happens in a different thread so that it
    runs in the background automatically. When the measurement is ended, its
    `multimeter.result.Result` can be retrieved from the measurement itself.

    Example:
        >>> multimeter = Multimeter(ResourceProbe())
        >>> measurement = multimeter.measure()
        >>> measurement.start()
        >>> here_my_code_to_be_measured()
        ...
        >>> measurement.end()
        >>> result = measurement.result

    Alternatively, `Measurement` can be used as a context manager, that returns the
    result:

    Example:
        >>> multimeter = Multimeter(ResourceProbe())
        >>> with multimeter.measure() as result:
        ...     here_my_code_to_be_measured()
        ...
    """

    def __init__(self, *probes, cycle_time=1.0, storage=DummyStorage()):
        """
        Create a new multi meter.

        Args:
            *probes (multimeter.probe.Probe): A list of probes that measure.
            cycle_time (float): The time in seconds between two measure points.
                Defaults to `1.0`. which means measure every second.
            storage (multimeter.storage.Storage): A instance of `Storage` that takes
                care of storing the final result. Defaults to an implementation that
                doesn't do anything.
        """
        self._cycle_time = cycle_time
        self._probes = [*probes]
        self._storage = storage

    def measure(self, identifier=None, **tags):
        """
        Create a new measurement based on the multimeters configuration.

        Args:
            identifier (str): The (unique) identifier for this measurement.
            **tags (Dict[str,str]): Optional user-defined tags, that can be used
                later for identifying the measurement.

        Returns:
            multimeter.measurement.Measurement: The new measurement object which is
                used for starting and ending the process.
        """
        return Measurement(self, identifier, **tags)

    @property
    def probes(self):
        """Returns the probes that gather the data."""
        return self._probes

    def add_probes(self, *probes):
        """
        Add probes that gather data.

        Args:
            *probes (multimeter.probe.Probe): Objects that implement the Probe
                protocol.

        Returns:
            Multimeter: The multimeter.
        """
        self._probes.extend(probes)
        return self

    @property
    def cycle_time(self):
        """Returns the cycle time in seconds, how often data is gathered."""
        return self._cycle_time

    def set_cycle_time(self, cycle_time):
        """
        Sets the cycle time, how often data is gathered.

        Args:
            cycle_time (float): The time between two sequential data gatherings.

        Returns:
            Multimeter: The multimeter.
        """
        self._cycle_time = cycle_time
        return self

    @property
    def storage(self):
        """Returns the storage."""
        return self._storage

    def set_storage(self, storage):
        """
        Sets the storage.

        Args:
            storage (multimeter.storage.Storage): The storage that stores the results.

        Returns:
            Multimeter: The multimeter.
        """
        self._storage = storage
        return self
