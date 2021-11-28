import datetime
import unittest

from multimeter.measure import Measure
from multimeter.metric import Metric
from multimeter.result import Point, Result
from multimeter.subject import Subject


class TestPoint(unittest.TestCase):

    def test_point_has_readable_repr(self):
        point = Point(datetime.datetime(2021, 1, 1, 1, 11, 11), {})
        self.assertEqual(repr(point), 'Point(datetime.datetime(2021, 1, 1, 1, 11, 11), {})')

    def test_point_has_readable_str(self):
        point = Point(datetime.datetime(2021, 1, 1, 1, 11, 11), {})
        self.assertEqual(str(point), "Point('2021-01-01T01:11:11.000', {})")


class TestResult(unittest.TestCase):

    def test_start_time_is_none_in_empty_sequence(self):
        result = Result()
        self.assertIsNone(result.start)

    def test_start_time_is_time_of_first_point(self):
        result = Result()
        result.append(datetime.datetime(2021, 1, 1, 1, 1), {})
        result.append(datetime.datetime(2021, 1, 1, 1, 10), {})
        self.assertEqual(result.start, datetime.datetime(2021, 1, 1, 1, 1))

    def test_end_time_is_none_in_empty_sequence(self):
        result = Result()
        self.assertIsNone(result.end)

    def test_end_time_is_time_of_last_point(self):
        result = Result()
        result.append(datetime.datetime(2021, 1, 1, 1, 1), {})
        result.append(datetime.datetime(2021, 1, 1, 1, 10), {})
        self.assertEqual(result.end, datetime.datetime(2021, 1, 1, 1, 10))

    def test_duration_is_none_in_empty_sequence(self):
        result = Result()
        self.assertIsNone(result.duration)

    def test_duration_is_time_between_first_and_last(self):
        result = Result()
        result.append(datetime.datetime(2021, 1, 1, 1, 1), {})
        result.append(datetime.datetime(2021, 1, 1, 1, 10), {})
        self.assertEqual(result.duration, datetime.timedelta(minutes=9))

    def test_values_returns_all_values_for_a_key(self):
        result = Result()
        result.append(datetime.datetime(2021, 1, 1, 1, 1), {'a': 1})
        result.append(datetime.datetime(2021, 1, 1, 1, 2), {'a': 2})
        result.append(datetime.datetime(2021, 1, 1, 1, 3), {'a': 3})
        values = result.values('a')
        self.assertEqual(list(values), [1, 2, 3])

    def test_metrics_can_be_added(self):
        metric = Metric("my_metric")
        result = Result()
        result._add_metrics([metric])
        self.assertIn(metric, result.metrics)

    def test_subject_can_be_added(self):
        subject = Subject("my_subject")
        result = Result()
        result._add_subjects([subject])
        self.assertIn(subject, result.subjects)

    def test_measures_can_be_added(self):
        metric = Metric("my_metric")
        subject = Subject("my_subject")
        measure = Measure(subject, metric)
        result = Result()
        result._add_measures([measure])
        self.assertIn(measure, result.measures)


if __name__ == '__main__':
    unittest.main()
