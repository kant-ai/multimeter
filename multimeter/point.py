"""Represent measurement values"""


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
