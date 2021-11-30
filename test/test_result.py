import datetime
import unittest

from multimeter.measure import Measure
from multimeter.metric import Metric
from multimeter.result import Mark, Point, Result, Schema
from multimeter.subject import Subject


class TestPoint(unittest.TestCase):

    def test_point_has_readable_repr(self):
        point = Point(datetime.datetime(2021, 1, 1, 1, 11, 11), {})
        self.assertEqual(repr(point), 'Point(datetime.datetime(2021, 1, 1, 1, 11, 11), {})')

    def test_point_has_readable_str(self):
        point = Point(datetime.datetime(2021, 1, 1, 1, 11, 11), {})
        self.assertEqual(str(point), "Point('2021-01-01T01:11:11.000', {})")


class TestMark(unittest.TestCase):

    def test_mark_has_readable_repr(self):
        mark = Mark(datetime.datetime(2021, 1, 1, 1, 11, 11), "My mark")
        self.assertEqual(repr(mark), "Mark(datetime.datetime(2021, 1, 1, 1, 11, 11), 'My mark')")

    def test_mark_has_readable_str(self):
        point = Mark(datetime.datetime(2021, 1, 1, 1, 11, 11), "My mark")
        self.assertEqual(str(point), "Mark('2021-01-01T01:11:11.000', My mark)")


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


class TestSchema(unittest.TestCase):

    def test_metrics_subject_measures_are_added_from_probe(self):
        metric = Metric("my_metric")
        subject = Subject("my_subject")
        measure = Measure(subject, metric)

        class MyProbe:

            @property
            def metrics(self):
                return tuple([metric])

            @property
            def subjects(self):
                return tuple([subject])

            @property
            def measures(self):
                return tuple([measure])

        schema = Schema([MyProbe()])

        self.assertIn(metric, schema.metrics)
        self.assertIn(subject, schema.subjects)
        self.assertIn(measure, schema.measures)


if __name__ == '__main__':
    unittest.main()
