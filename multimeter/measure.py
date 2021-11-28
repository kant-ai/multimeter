"""Contains Measure class"""


class Measure:
    """
    Class that represents a metric that is gathered on a subject.

    Attributes:
        key (str): The (unique) key that is used for referencing a measure. The key is
            derived from the keys of the subject and the metric in the form
            `<subject-key>.<metric-key>`.
        subject (multimeter.subject.Subject): The subject on which the measure gathers
            data.
        metric (multimeter.metric.Metric): The metric which is gathered.
    """

    def __init__(self, subject, metric):
        self.key = subject.key + '.' + metric.key
        self.subject = subject
        self.metric = metric

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)
