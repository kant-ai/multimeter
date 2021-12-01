import subprocess
import sys
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

    def test_started_measurement_doesnt_block_exit(self):
        subprocess.check_call([
            sys.executable,
            '-c',
            'import multimeter; m = multimeter.Multimeter(cycle_time=0.1).measure(""); m.start();'
        ], timeout=1.0)

    def test_measurement_can_add_marks_to_result(self):
        mm = Multimeter(cycle_time=0.01)
        with mm.measure() as measurement:
            measurement.add_mark("First mark")
            time.sleep(0.02)
            measurement.add_mark("Second mark")
        self.assertEqual(measurement.result.marks[0].label, "First mark")
        self.assertEqual(measurement.result.marks[1].label, "Second mark")


if __name__ == '__main__':
    unittest.main()
