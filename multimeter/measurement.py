"""Measuring run-time properties"""
import datetime
import logging
import threading
import time

from .result import Result


logger = logging.getLogger(__name__)


class Measurement:
    """
    Class that is used for a single series of measurement.

    Attributes:
        identifier (str): The (unique) identifier for this series of measurement.
        tags (Dict[str,str]): A set of user-defined tags that can be used for later
            differentiation between different series.
        result (multimeter.result.Result): The result of the series of measurement
            containing the measured values.
    """

    def __init__(self, multimeter, identifier, **tags):
        """
        Creates a new measurement.

        Args:
            multimeter (multimeter.multimeter.Multimeter): The multimeter whose
                configuration should be used for this measurement.
            identifier: The (unique) identifier for this series of measurement. If
                `None`, a unique identifier is generated from the current time.
            **tags (Dict[str,str]): A set of user-defined tags that can be used
                for later differentiation between different measurements.
        """
        self.identifier = identifier or str(time.time())
        self.tags = tags
        self.result = None
        self._probes = multimeter.probes
        self._storage = multimeter.storage
        self._thread = _MeasuringThread(self._sample, cycle_time=multimeter.cycle_time)
        self._time_last_sample = None

    def start(self):
        """
        Starts the process of gathering run-time property values.

        Returns:
            multimeter.result.Result: The result of this series of measurement.
        """
        self.result = Result(*self._probes, identifier=self.identifier, tags=self.tags)
        self._time_last_sample = time.monotonic()
        for probe in self._probes:
            probe.start()
        self._thread.start()
        return self.result

    def end(self):
        """
        Ends the process of gathering run-time property values.

        """
        self._thread.end()
        self._thread.join()
        for probe in self._probes:
            probe.end()
        self._storage.store(self.result)

    def add_mark(self, label):
        """
        Add a new mark for the current time.

        Args:
            label (str): The label of the mark.
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        self.result.add_mark(timestamp, label)

    def _sample(self):
        """Gathers the measures for the current timestamp."""
        time_current_sample = time.monotonic()
        time_elapsed = time_current_sample - self._time_last_sample
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        values = {}
        for probe in self._probes:
            probe.sample(values, time_elapsed)
        logger.debug("For %s sampled values %s", timestamp, values)
        self.result.append(timestamp, values)
        self._time_last_sample = time_current_sample

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, error_type, value, traceback):
        self.end()


class _MeasuringThread(threading.Thread):
    """
    Thread that runs in parallel and samples the data.
    """

    def __init__(self, sample_function, cycle_time=1.0):
        self._stop_event = threading.Event()
        self._sample_function = sample_function
        self._cycle_time = cycle_time
        self._last_cycle_duration = cycle_time
        super().__init__(daemon=True)

    def end(self):
        """Signals to the thread that it should end."""
        self._stop_event.set()

    def run(self):
        last_measure_time = None
        delta = 0.0
        while not self._stop_event.is_set():
            current_time = time.monotonic()
            logger.debug("Sampling at %f", current_time)
            self._sample_function()
            if last_measure_time is not None:
                delta += current_time - last_measure_time - self._cycle_time
            last_measure_time = current_time
            logger.debug("Delta %f", delta)
            corrected_sleep_time = self._cycle_time - delta
            if corrected_sleep_time <= 0.0:
                logger.warning("Sampling lagging behind cycle time, ignore sleep")
                delta = 0.0
            else:
                logger.debug("Sleeping for %f seconds", corrected_sleep_time)
                self._stop_event.wait(corrected_sleep_time)
        self._sample_function()
