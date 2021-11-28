import unittest

from multimeter.metric import Metric
from multimeter.measure import Measure
from multimeter.subject import Subject


class TestMeasure(unittest.TestCase):

    def setUp(self):
        self.subject = Subject('subject')
        self.metric = Metric('metric')

    def test_key_derived_from_metric_and_subject(self):
        m = Measure(self.subject, self.metric)
        self.assertEqual('subject.metric', m.key)

    def test_same_key_same_hash(self):
        m1 = Measure(self.subject, self.metric)
        m2 = Measure(self.subject, self.metric)
        self.assertEqual(hash(m1), hash(m2))

    def test_same_key_equals(self):
        m1 = Measure(self.subject, self.metric)
        m2 = Measure(self.subject, self.metric)
        self.assertEqual(m1, m2)


if __name__ == '__main__':
    unittest.main()
