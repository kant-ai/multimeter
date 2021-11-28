"""Contains the protocol for probes which gather the data"""
import abc
import resource

from .measure import Measure
from .metric import (
    METRIC_CPU_RATE_USER,
    METRIC_CPU_RATE_SYSTEM,
    METRIC_MEMORY_MAX,
    METRIC_MEMORY_SHARED,
    METRIC_MEMORY_DATA,
    METRIC_MEMORY_STACK,
    METRIC_MEMORY_PAGE_FAULTS_WITH_IO,
    METRIC_MEMORY_PAGE_FAULTS_WITHOUT_IO,
    METRIC_MEMORY_SWAP_OPS,
    METRIC_IO_BLOCK_IN,
    METRIC_IO_BLOCK_OUT,
    METRIC_CONTEXT_SWITCHES_VOL,
    METRIC_CONTEXT_SWITCHES_INVOL,
)
from .subject import SUBJECT_PROCESS, SUBJECT_CHILDREN


class Probe(abc.ABC):
    """
    Protocol that is used for gathering run-time properties.
    """

    @property
    def metrics(self):
        """
        The metrics used by this probe.

        Returns:
            tuple[multimeter.metric.Metric]: A tuple of metrics that are gathered by
                this probe.
        """
        return tuple()

    @property
    def subjects(self):
        """
        The subjects from which measures will be gathered.

        Returns:
            tuple[multimeter.subject.Subject]: A tuple of subjects from which data is
                gathered by this probe.
        """
        return tuple()

    @property
    def measures(self):
        """
        The measures that will be gathered.

        Returns:
            tuple[multimeter.measure.Measure]: A tuple of measures from which data is
                gathered by this probe.
        """
        return tuple()

    def start(self):
        """
        Signals to the probe that it should start the gathering process.
        """

    @abc.abstractmethod
    def sample(self, values, time_elapsed):
        """
        Sample all measures of this probe and store their current values.

        Args:
            values (Dict[str,any]): The dictionary where the values should be stored.
                The probe is expected to add the values for every measure under their
                key.
            time_elapsed (float): Time elapsed in seconds since the last sampling.
        """

    def end(self):
        """
        Signals to the probe that the gathering process is ended.
        """


class ResourceProbe(Probe):
    """Probe which gathers data using the python `resource` module."""

    # for more information about the different metrics, take a look at
    # https://www.gnu.org/software/libc/manual/html_node/Resource-Usage.html
    _METRICS = (
        METRIC_CPU_RATE_USER,
        METRIC_CPU_RATE_SYSTEM,
        METRIC_MEMORY_MAX,
        METRIC_MEMORY_SHARED,
        METRIC_MEMORY_DATA,
        METRIC_MEMORY_STACK,
        METRIC_MEMORY_PAGE_FAULTS_WITH_IO,
        METRIC_MEMORY_PAGE_FAULTS_WITHOUT_IO,
        METRIC_MEMORY_SWAP_OPS,
        METRIC_IO_BLOCK_IN,
        METRIC_IO_BLOCK_OUT,
        METRIC_CONTEXT_SWITCHES_VOL,
        METRIC_CONTEXT_SWITCHES_INVOL,
    )

    _SUBJECTS = (
        SUBJECT_PROCESS,
        SUBJECT_CHILDREN,
    )

    _metric_to_field = {
        'cpu_rate_user': 'ru_utime',
        'cpu_rate_system': 'ru_stime',
        'memory_rss_max': 'ru_maxrss',
        'memory_rss_shared': 'ru_ixrss',
        'memory_rss_data': 'ru_idrss',
        'memory_rss_stack': 'ru_isrss',
        'memory_page_faults_without_io': 'ru_minflt',
        'memory_page_faults_with_io': 'ru_majflt',
        'memory_swap_ops': 'ru_nswap',
        'io_block_in': 'ru_inblock',
        'io_block_out': 'ru_oublock',
        'context_switches_vol': 'ru_nvcsw',
        'context_switches_invol': 'ru_nivcsw',
    }

    def __init__(self):
        self._last_process_values = None
        self._last_children_values = None
        self._measures = tuple(
            Measure(subject, metric)
            for subject in ResourceProbe._SUBJECTS
            for metric in ResourceProbe._METRICS
        )

    @property
    def metrics(self):
        return ResourceProbe._METRICS

    @property
    def subjects(self):
        return ResourceProbe._SUBJECTS

    @property
    def measures(self):
        return self._measures

    def start(self):
        self._last_process_values = resource.getrusage(resource.RUSAGE_SELF)
        self._last_children_values = resource.getrusage(resource.RUSAGE_CHILDREN)

    def sample(self, values, time_elapsed):
        if self._last_process_values is None or self._last_children_values is None:
            raise RuntimeError("Need to start before sampling.")

        usage = resource.getrusage(resource.RUSAGE_SELF)
        self._add_to_data(
            values, 'process.', usage, self._last_process_values, time_elapsed
        )
        self._last_process_values = usage
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        self._add_to_data(
            values, 'children.', usage, self._last_children_values, time_elapsed
        )
        self._last_children_values = usage

    @staticmethod
    def _add_to_data(values, prefix, usage, previous_usage, time_elapsed):
        for key, field in ResourceProbe._metric_to_field.items():
            if key in {
                'memory_rss_max',
                'memory_rss_shared',
                'memory_rss_data',
                'memory_rss_stack',
            }:
                values[prefix + key] = getattr(usage, field)
            else:
                values[prefix + key] = (
                    getattr(usage, field) - getattr(previous_usage, field)
                ) / time_elapsed
