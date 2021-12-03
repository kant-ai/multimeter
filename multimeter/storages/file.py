"""Storage that stores results in files"""
import abc
import io
import itertools
import json
import pathlib

from .base import Storage


class FileFormat(abc.ABC):
    """
    Abstract base class for the different file format implementations.
    """

    @property
    @abc.abstractmethod
    def extension(self):
        """Returns the file extensions for the file, e.g. '.json'."""

    @abc.abstractmethod
    def save_result_to_stream(self, result, stream):
        """
        Saves the result to a binary stream.

        Args:
            result (multimeter.result.Result): The result.
            stream (io.RawIOBase): Binary stream where the result is written to.
        """


class FileStorage(Storage):
    """
    Storage implementation that stores results as JSON files in a directory.

    Attributes:
        save_directory (pathlib.Path): The path to the directory where the results are
            stored.
        file_format (multimeter.storages.file.FileFormat): The file format to use.
    """

    def __init__(self, save_directory, file_format):
        """
        Creates a new file storage.

        Args:
            save_directory (Union[str,pathlib.Path]): The path to a directory, where
                the json files will be stored.
            file_format (FileFormat): The format to use for the file.
        """
        if save_directory is None:
            raise ValueError("'save_directory' must be set.")
        if not isinstance(save_directory, pathlib.Path):
            save_directory = pathlib.Path(save_directory)
        self._save_directory = save_directory
        self._file_format = file_format

    @property
    def save_directory(self):
        """Returns the save directory."""
        return self._save_directory

    def store(self, result):
        if not self._save_directory.exists():
            self._save_directory.mkdir(parents=True)
        result_file_path = self._save_directory / (
            result.identifier + self._file_format.extension
        )
        with open(result_file_path, 'bw') as stream:
            self._file_format.save_result_to_stream(result, stream)


class _SerializableGenerator(list):
    """Generator that is serializable by JSON"""

    def __init__(self, iterable):
        super().__init__()
        tmp_body = iter(iterable)
        try:
            self._head = iter([next(tmp_body)])
            self.append(tmp_body)
        except StopIteration:
            self._head = []

    def __iter__(self):
        return itertools.chain(self._head, *self[:1])


class JsonFormat(FileFormat):
    """
    Format implementation that stores results as JSON.
    """

    @property
    def extension(self):
        return '.json'

    def save_result_to_stream(self, result, stream):
        """
        Saves the result to a (binary) stream.

        Args:
            result (multimeter.result.Result): The result to save.
            stream (io.RawIOBase): The binary stream into which the result data should
                be written. The stream is not automatically closed.
        """
        text_stream = io.TextIOWrapper(stream, encoding='utf-8')

        metrics_json = _SerializableGenerator(
            {
                'key': o.key,
                'description': o.description,
                'unit': o.unit,
                'value_type': o.value_type.__name__,
                'min_value': o.min_value,
                'max_value': o.max_value,
            }
            for o in result.schema.metrics
        )
        subjects_json = _SerializableGenerator(
            {
                'key': o.key,
                'description': o.description,
            }
            for o in result.schema.subjects
        )
        measures_json = _SerializableGenerator(
            {
                'key': o.key,
                'subject': o.subject.key,
                'metric': o.metric.key,
            }
            for o in result.schema.measures
        )
        points_json = _SerializableGenerator(
            {
                'datetime': o.datetime.isoformat(timespec='milliseconds'),
                'values': o.values,
            }
            for o in result.points
        )
        marks_json = _SerializableGenerator(
            {
                'datetime': o.datetime.isoformat(timespec='milliseconds'),
                'label': o.label,
            }
            for o in result.marks
        )
        result_json = {
            'identifier': result.identifier,
            'tags': result.tags,
            'meta_data': result.meta_data,
            'schema': {
                'metrics': metrics_json,
                'subjects': subjects_json,
                'measures': measures_json,
            },
            'points': points_json,
            'marks': marks_json,
        }
        json.dump(result_json, text_stream, indent=2)
        text_stream.detach()


class LineFormat(FileFormat):
    """
    Format implementation that stores results as Line format.

    The format is used by time series databases like InfluxDB. For more information:
    https://docs.influxdata.com/influxdb/v2.1/reference/syntax/line-protocol/#string
    """

    @property
    def extension(self):
        return '.line'

    @staticmethod
    def _check_measurement_identifier(identifier):
        if identifier == '':
            raise ValueError("Identifier can't be empty.")
        if identifier[0] == '_':
            raise ValueError("Identifier can't start with '_'.")
        if '\n' in identifier:
            raise ValueError("Identifier can't contain line breaks.")

    @staticmethod
    def _escape_identifier(identifier):
        return identifier.replace(',', r'\,').replace(' ', r'\ ')

    @staticmethod
    def _value_as_string(value):
        if type(value) is str:  # pylint: disable=unidiomatic-typecheck
            value = value.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{value}"'
        # don't use instanceof to make sure we don't handle boolean
        if type(value) is int:  # pylint: disable=unidiomatic-typecheck
            return f'{value}i'
        return str(value)

    @staticmethod
    def _escape_field_key(key):
        return key.replace(',', r'\,').replace('=', r'\=').replace(' ', r'\ ')

    @staticmethod
    def _escape_tag(value):
        return value.replace(',', r'\,').replace('=', r'\=').replace(' ', r'\ ')

    def save_result_to_stream(self, result, stream):
        """
        Saves the result to a (binary) stream.

        Args:
            result (multimeter.result.Result): The result to save.
            stream (io.RawIOBase): The binary stream into which the result data should
                be written. The stream is not automatically closed.
        """
        self._check_measurement_identifier(result.identifier)
        text_stream = io.TextIOWrapper(stream, encoding='utf-8')
        tags = ''.join(
            f",{self._escape_tag(key)}={self._escape_tag(value)}"
            for key, value in result.tags.items()
        )
        identifier = self._escape_identifier(result.identifier)
        for point in result.points:
            values = ','.join(
                f'{self._escape_field_key(key)}={self._value_as_string(value)}'
                for key, value in point.values.items()
            )
            # convert from seconds to nano
            timestamp = int(point.datetime.timestamp() * 1000 * 1000 * 1000)
            text_stream.write(f'{identifier}{tags} {values} {timestamp}\n')

        text_stream.detach()
