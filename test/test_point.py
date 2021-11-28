import datetime
import unittest

from multimeter.point import Point


class TestPoint(unittest.TestCase):

    def test_point_has_readable_repr(self):
        point = Point(datetime.datetime(2021, 1, 1, 1, 11, 11), {})
        self.assertEqual(repr(point), 'Point(datetime.datetime(2021, 1, 1, 1, 11, 11), {})')

    def test_point_has_readable_str(self):
        point = Point(datetime.datetime(2021, 1, 1, 1, 11, 11), {})
        self.assertEqual(str(point), "Point('2021-01-01T01:11:11.000', {})")


if __name__ == '__main__':
    unittest.main()
