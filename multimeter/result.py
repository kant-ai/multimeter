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


class Mark:
    """
    Class that contains a mark for a specified time with an annotation.

    Attributes:
        datetime (datetime.datetime): The timestamp in UTC.
        label (str): The annotation of the mark.
    """

    __slots__ = [
        'datetime',
        'label',
    ]

    def __init__(self, datetime, label):
        self.datetime = datetime
        self.label = label

    def __repr__(self):
        return f"Mark({repr(self.datetime)}, {repr(self.label)})"

    def __str__(self):
        datetime_str = self.datetime.isoformat(timespec='milliseconds')
        return f"Mark('{datetime_str}', {self.label})"


class Schema:
    """
    Class that represents the schema of the values in a result.

    The schema consists of the used metrics, the subjects of the measures and the
    measures, which define which metric is measured on which subject.

    Attributes:
        metrics (tuple[multimeter.metric.Metric): A list of metrics which are measured.
        subjects (tuple[multimeter.subject.Subject): A list of subjects on which some
            metrics were measured.
        measures (tuple[multimeter.measure.Measure): A list of measures, which contains
            which metrics were measured on which subjects.
    """

    def __init__(self, probes):
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


class Result:
    """
    Class representing results of a measurement.

    Attributes:
        identifier (str): A string, that identifies the measurement.
        tags (Dict[string,string]): A set of user-defined tags with arbitrary
            string values.
        meta_data (Dict[string,string]): A dictionary with meta data about the
            measurement.
        schema (multimeter.result.Schema): The schema of the values that are used in
            this result.
        points (tuple[multimeter.result.Point): A list of measurement points, which
            contain the measured values with their timestamp.
        marks (tuple[multimeter.result.Mark): A tuple of marks that were set at specific
            times during measuring.
    """

    def __init__(self, *probes, identifier=None, tags=None):
        self.identifier = identifier
        self.tags = tags or {}
        self.meta_data = {}
        self.schema = Schema(probes)
        self._points = []
        self._marks = []

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
    def marks(self):
        """Returns a tuple containing the marks"""
        return tuple(self._marks)

    def add_mark(self, timestamp, label):
        """
        Add a new mark for the given timestamp.

        Args:
            timestamp (datetime.datetime): The timestamp when the values were sampled.
            label (str): The label of the mark.
        """
        self._marks.append(Mark(timestamp, label))

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
