"""Contains classes for representing the results of a measurement"""


class Result:
    """
    Class representing results of a measurement.

    Attributes:
        identifier (str): A string, that identifies the measurement.
        labels (Dict[string,string]): A set of user-defined labels with arbitrary
            string values.
        meta (Dict[string,string]): A dictionary with meta data about the measurement.
        metrics (List[multimeter.metric.Metric): A list of metrics which are measured.
        subjects (List[multimeter.subject.Subject): A list of subjects on which some
            metrics were measured.
        measures (List[multimeter.measure.Measure): A list of measures, which contains
            which metrics were measured on which subjects.
        points (List[multimeter.point.Point): A list of measurement points, which
            contain the measured values with their timestamp.
    """

    def __init__(self, identifier=None, labels=None):
        self.identifier = identifier
        self.labels = labels or {}
        self.meta = {}
        self.metrics = []
        self.subjects = []
        self.measures = []
        self.points = []

    def add_meta_data(self, **meta_data):
        """
        Adds meta data to the result.

        Setting a value for a key the second time, will overwrite the value set the
        first time.

        Keyword Args:
            **meta_data: The set of meta data in form of keyword args that should be
                added to the result.
        """
        self.meta.update(**meta_data)

    def add_metrics(self, metrics):
        """
        Adds new metrics to the result.

        Args:
            metrics List[multimeter.metric.Metric]: A list of metrics.
        """
        self.metrics.extend(metrics)

    def add_subjects(self, subjects):
        """
        Adds new subjects to the result.

        Args:
            metrics List[multimeter.subject.Subject]: A list of subjects.
        """
        self.subjects.extend(subjects)

    def add_measures(self, measures):
        """
        Adds new measures to the result.

        Args:
            metrics List[multimeter.measure.Measure]: A list of measures.
        """
        self.measures.extend(measures)

    def append(self, point):
        """
        Add a new point with measured values to the result.

        Args:
            point (multimeter.point.Point): The point with the values.
        """
        self.points.append(point)

    @property
    def start(self):
        """
        Returns:
            datetime.datetime: The timestamp of the first measurement or `None` if
                nothing was measured.
        """
        if self.points:
            return self.points[0].datetime
        return None

    @property
    def end(self):
        """
        Returns:
            datetime.datetime: The timestamp of the last measurement or `None` if
                nothing was measured.
        """
        if self.points:
            return self.points[-1].datetime
        return None

    @property
    def duration(self):
        """
        Returns:
            datetime.timedelta: The duration between first and last measurement or
                `None` if nothing was measured.
        """
        if self.points:
            return self.points[-1].datetime - self.points[0].datetime
        return None

    def values(self, key):
        """
        Returns all values of a specific measure.

        Args:
            key (str): Key of the measure for which all values should be returned.

        Yields:
            any: A value of the type defined by the metric.
        """
        return (point.values[key] for point in self.points)
