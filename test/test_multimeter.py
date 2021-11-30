import unittest

from multimeter.multimeter import Multimeter
from multimeter.probe import ResourceProbe
from multimeter.storages.dummy import DummyStorage


class TestMultimeter(unittest.TestCase):

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
