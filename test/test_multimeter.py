import time
import unittest

from multimeter.multimeter import Multimeter
from multimeter.probe import ResourceProbe
from multimeter.result import Result
from multimeter.storages.dummy import DummyStorage


class TestMultimeterCase(unittest.TestCase):

    def test_measure_works_as_context_manager(self):
        mm = Multimeter(ResourceProbe(), cycle_time=0.01)
        with mm.measure() as result:
            time.sleep(0.1)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Result)

    def test_measure_works_with_cycle_time_of_0(self):
        mm = Multimeter(ResourceProbe(), cycle_time=0.0)
        with mm.measure() as result:
            time.sleep(0.01)
        self.assertIsNotNone(result)

    def test_measure_works_with_start_and_end(self):
        mm = Multimeter(ResourceProbe(), cycle_time=0.01)
        measurement = mm.measure()
        measurement.start()
        time.sleep(0.1)
        measurement.end()
        self.assertIsNotNone(measurement.result)

    def test_probes_can_be_added_later(self):
        mm = Multimeter(cycle_time=0.01)
        self.assertEqual(0, len(mm.probes))
        mm.add_probes(ResourceProbe())
        self.assertEqual(1, len(mm.probes))

    def test_cycle_time_can_be_set_later(self):
        mm = Multimeter()
        self.assertEqual(1.0, mm.cycle_time)
        mm.set_cycle_time(0.01)
        self.assertEqual(0.01, mm.cycle_time)

    def test_storage_can_be_set_later(self):
        my_storage = DummyStorage()
        mm = Multimeter()
        self.assertIsNot(my_storage, mm.storage)
        mm.set_storage(my_storage)
        self.assertIs(my_storage, mm.storage)


if __name__ == '__main__':
    unittest.main()
