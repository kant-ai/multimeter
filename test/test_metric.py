import sys
import unittest

from multimeter.metric import Metric


class TestMetric(unittest.TestCase):

    def test_same_key_same_hash(self):
        m1 = Metric('my_metric')
        m2 = Metric('my_metric')
        self.assertEqual(hash(m1), hash(m2))

    def test_same_key_equals(self):
        m1 = Metric('my_metric')
        m2 = Metric('my_metric')
        self.assertEqual(m1, m2)

    def test_metric_limits_value_to_min(self):
        m = Metric('metric', min_value=0.1)
        value = 0.0
        result = m.limit_value(value)
        self.assertEqual(0.1, result)

    def test_metric_limits_value_to_0_default(self):
        m = Metric('metric')
        value = -1.0
        result = m.limit_value(value)
        self.assertEqual(0.0, result)

    def test_metric_doesnt_limit_value_when_min_None(self):
        m = Metric('metric', min_value=None)
        value = -1.0
        result = m.limit_value(value)
        self.assertEqual(-1.0, result)

    def test_metric_limits_value_to_max(self):
        m = Metric('metric', max_value=0.1)
        value = 0.2
        result = m.limit_value(value)
        self.assertEqual(0.1, result)

    def test_metric_doesnt_limits_value_max_as_default(self):
        m = Metric('metric')
        value = sys.float_info.max
        result = m.limit_value(value)
        self.assertEqual(sys.float_info.max, result)

    def test_metric_doesnt_limit_value_when_max_None(self):
        m = Metric('metric', max_value=None)
        value = sys.float_info.max
        result = m.limit_value(value)
        self.assertEqual(sys.float_info.max, result)


if __name__ == '__main__':
    unittest.main()
