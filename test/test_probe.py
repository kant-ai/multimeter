import unittest

from multimeter.probe import Probe, ResourceProbe
from multimeter.measure import Measure


class DummyProbe(Probe):

    def sample(self, values, time_elapsed):
        pass


class TestProbe(unittest.TestCase):

    def test_probe_cant_be_instantiated(self):
        with self.assertRaisesRegex(TypeError, ""):
            Probe()

    def test_probe_with_implemented_sample_can_be_instantiated(self):
        probe = DummyProbe()
        self.assertIsNotNone(probe)

    def test_dummy_probe_returns_empty_metrics(self):
        probe = DummyProbe()
        self.assertEqual(tuple(), probe.metrics)

    def test_dummy_probe_returns_empty_subjects(self):
        probe = DummyProbe()
        self.assertEqual(tuple(), probe.subjects)

    def test_dummy_probe_returns_empty_measures(self):
        probe = DummyProbe()
        self.assertEqual(tuple(), probe.measures)


class TestResourceProbe(unittest.TestCase):

    def test_probe_can_be_instantiated(self):
        probe = ResourceProbe()
        self.assertIsNotNone(probe)

    def test_probe_returns_non_empty_metrics(self):
        probe = ResourceProbe()
        self.assertNotEqual(tuple(), probe.metrics)

    def test_probe_returns_subjects_for_process_and_children(self):
        probe = ResourceProbe()
        subjects = probe.subjects
        self.assertEqual('process', subjects[0].key)
        self.assertEqual('children', subjects[1].key)

    def test_probe_returns_measures_for_all_subjects_and_metrics(self):
        probe = ResourceProbe()
        subjects = probe.subjects
        metrics = probe.metrics
        measures = probe.measures
        for subject in subjects:
            for metric in metrics:
                self.assertIn(Measure(subject, metric), measures)
        self.assertEqual(len(metrics)*len(subjects), len(measures))

    def test_sampling_before_start_raises_error(self):
        probe = ResourceProbe()
        with self.assertRaisesRegex(RuntimeError, "Need to start"):
            probe.sample({}, 1.0)

    def test_sample_adds_value_for_every_measure(self):
        probe = ResourceProbe()
        probe.start()
        values = {}
        probe.sample(values, 1.0)
        for measure in probe.measures:
            self.assertIn(measure.key, values)


if __name__ == '__main__':
    unittest.main()
