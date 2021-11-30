"""Contains classes for representing the results of a measurement"""


class Point:
    """
    Class that contains the values of a single measurement point.

    Attributes:
        datetime (datetime.datetime): The timestamp in UTC.
        values (dict[string, any]): The
    """

    __slots__ = [
        'datetime',
        'values',
    ]

    def __init__(self, datetime, values):
        self.datetime = datetime
        self.values = values

    def __repr__(self):
        return f"Point({repr(self.datetime)}, {repr(self.values)})"

    def __str__(self):
        datetime_str = self.datetime.isoformat(timespec='milliseconds')
        return f"Point('{datetime_str}', {self.values})"


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

    def __init__(self, *probes, identifier=None, labels=None):
        self.identifier = identifier
        self.labels = labels or {}
        self.meta_data = {}
        self._points = []
        metrics = []
        subjects = []
        measures = []
        for probe in probes:
            metrics.extend(probe.metrics)
            subjects.extend(probe.subjects)
            measures.extend(probe.measures)
        self.metrics = tuple(metrics)
        self.subjects = tuple(subjects)
        self.measures = tuple(measures)

    def add_meta_data(self, **meta_data):
        """
        Adds meta data to the result.

        Setting a value for a key the second time, will overwrite the value set the
        first time.

        Keyword Args:
            **meta_data: The set of meta data in form of keyword args that should be
                added to the result.
        """
        self.meta_data.update(**meta_data)

    @property
    def points(self):
        """Returns a tuple containing the points"""
        return tuple(self._points)

    def append(self, timestamp, values):
        """
        Add a new point with measured values to the result.

        Args:
            timestamp (datetime.datetime): The timestamp when the values were sampled.
            values (Dict[str,any]): The values.
        """
        self._points.append(Point(timestamp, values))

    @property
    def start(self):
        """
        Returns:
            datetime.datetime: The timestamp of the first measurement or `None` if
                nothing was measured.
        """
        if self._points:
            return self._points[0].datetime
        return None

    @property
    def end(self):
        """
        Returns:
            datetime.datetime: The timestamp of the last measurement or `None` if
                nothing was measured.
        """
        if self._points:
            return self._points[-1].datetime
        return None

    @property
    def duration(self):
        """
        Returns:
            datetime.timedelta: The duration between first and last measurement or
                `None` if nothing was measured.
        """
        if self._points:
            return self._points[-1].datetime - self._points[0].datetime
        return None

    def values(self, key):
        """
        Returns all values of a specific measure.

        Args:
            key (str): Key of the measure for which all values should be returned.

        Yields:
            any: A value of the type defined by the metric.
        """
        return (point.values[key] for point in self._points)
