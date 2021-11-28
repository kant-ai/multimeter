"""Metrics that define the type of measured values"""
import sys


class Metric:
    """
    Class representing a metric describing the type of measured values.

    Attributes:
        key (str): The (unique) key that is used for referencing a metric.
        description (str): A human readable description of the metric. Defaults to the
            empty string `""`.
        unit (str): The unit in which the value of metric is expressed. Defaults to
            the empty string `""`.
        value_type (type): The python type used for the values of this metric.
            Defaults to `float`.
        min_value (value_type): The minimum value that this metric can produce.
            Defaults to `0.0`, but can be set to `None` to disable limitation.
        max_value (value_type): The maximum value that this metric can produce.
            Defaults to `None` which disables limitation.

    """

    def __init__(
        self,
        key,
        description="",
        unit="",
        value_type=float,
        min_value=0.0,
        max_value=sys.float_info.max,
    ):  # pylint: disable=too-many-arguments
        self.key = key
        self.description = description
        self.unit = unit
        self.value_type = value_type
        self.min_value = min_value
        self.max_value = max_value

    def limit_value(self, value):
        """
        Make sure the value is in the limits of this metric.

        If the given value is larger than `max_value` or smaller than `min_value` the
        value is capped.

        Args:
            value (value_type): The value tp limit.

        Returns:
            value_type: The limited value.
        """
        if self.min_value is not None:
            value = max(self.min_value, value)
        if self.max_value is not None:
            value = min(self.max_value, value)
        return value

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)


METRIC_MEMORY_SWAP_OPS = Metric(
    key='memory_swap_ops',
    description="The number of times per second the process was swapped "
    "entirely out of main memory.",
    value_type=float,
    max_value=None,
)

METRIC_MEMORY_PAGE_FAULTS_WITHOUT_IO = Metric(
    key='memory_page_faults_without_io',
    description="The number of page faults per second which were serviced by "
    "doing I/O.",
    value_type=float,
    max_value=None,
)

METRIC_MEMORY_PAGE_FAULTS_WITH_IO = Metric(
    key='memory_page_faults_without_io',
    description="The number of page faults per second which were serviced "
    "without requiring any I/O.",
    value_type=float,
    max_value=None,
)

METRIC_MEMORY_STACK = Metric(
    key='memory_rss_stack',
    description="The amount of unshared memory used for stack space.",
    value_type=int,
    unit='kB',
    max_value=None,
)

METRIC_MEMORY_DATA = Metric(
    key='memory_rss_data',
    description="The amount of unshared memory used for data.",
    value_type=int,
    unit='kB',
    max_value=None,
)

METRIC_MEMORY_SHARED = Metric(
    key='memory_rss_shared',
    description="The size of the shared memory.",
    value_type=int,
    unit='kB',
    max_value=None,
)

METRIC_MEMORY_MAX = Metric(
    key='memory_rss_max',
    description="The maximum resident set size in memory.",
    value_type=int,
    unit='kB',
    max_value=None,
)

METRIC_CPU_RATE_SYSTEM = Metric(
    key='cpu_rate_system',
    description="The rate of the time where the CPU is executing system " "code.",
    max_value=1.0,
)

METRIC_CPU_RATE_USER = Metric(
    key='cpu_rate_user',
    description="The rate of the time where the CPU is executing user-space " "code.",
    max_value=1.0,
)

METRIC_IO_BLOCK_IN = Metric(
    key='io_block_in',
    description="The number of times per second the file system had to read "
    "from the disk.",
    value_type=float,
    max_value=None,
)

METRIC_IO_BLOCK_OUT = Metric(
    key='io_block_out',
    description="The number of times per second the file system had to write "
    "to the disk.",
    value_type=float,
    max_value=None,
)

METRIC_CONTEXT_SWITCHES_VOL = Metric(
    key='context_switches_vol',
    description="The number of times per second a context switch was "
    "voluntarily invoked.",
    value_type=float,
    max_value=None,
)

METRIC_CONTEXT_SWITCHES_INVOL = Metric(
    key='context_switches_invol',
    description="The number of times per second an involuntary context "
    "switch took place.",
    value_type=float,
    max_value=None,
)
