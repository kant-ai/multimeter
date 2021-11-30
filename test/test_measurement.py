import time
import unittest

from multimeter.measurement import Measurement
from multimeter.multimeter import Multimeter
from multimeter.probe import ResourceProbe
from multimeter.result import Result


class TestMeasurement(unittest.TestCase):

    def test_measure_works_as_context_manager(self):
        mm = Multimeter(ResourceProbe(), cycle_time=0.01)
        with mm.measure() as measurement:
            time.sleep(0.1)
        self.assertIsNotNone(measurement)
        self.assertIsInstance(measurement, Measurement)
        self.assertIsNotNone(measurement.result)
        self.assertIsInstance(measurement.result, Result)

    def test_measure_works_with_cycle_time_of_0(self):
        mm = Multimeter(ResourceProbe(), cycle_time=0.0)
        with mm.measure() as measurement:
            time.sleep(0.01)
        self.assertIsNotNone(measurement)

    def test_measure_works_with_start_and_end(self):
        mm = Multimeter(ResourceProbe(), cycle_time=0.01)
        measurement = mm.measure()
        measurement.start()
        time.sleep(0.1)
        measurement.end()
        self.assertIsNotNone(measurement.result)


if __name__ == '__main__':
    unittest.main()
