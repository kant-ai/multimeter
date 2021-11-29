"""Storage that stores results in JSON files"""
import itertools
import json
import pathlib

from .base import Storage


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


class JsonFileStorage(Storage):
    """
    Storage implementation that stores results as JSON files in a directory.

    Attributes:
        save_directory (pathlib.Path): The path to the directory where the results are
            stored.
    """

    def __init__(self, save_directory):
        """
        Creates a new json file storage.

        Args:
            save_directory (Union[str,pathlib.Path]): The path to a directory, where
                the json files will be stored.
        """
        if save_directory is None:
            raise ValueError("'save_directory' must be set.")
        if not isinstance(save_directory, pathlib.Path):
            save_directory = pathlib.Path(save_directory)
        self._save_directory = save_directory

    @property
    def save_directory(self):
        """Returns the save directory."""
        return self._save_directory

    def store(self, result):
        if not self._save_directory.exists():
            self._save_directory.mkdir(parents=True)
        result_file_path = self._save_directory / (result.identifier + '.json')
        with open(result_file_path, 'w', encoding='utf-8') as stream:
            self._save_result_to_stream(result, stream)

    @staticmethod
    def _save_result_to_stream(result, stream):
        """
        Saves the result to a (binary) stream.

        Args:
            stream (io.RawIOBase): The binary stream into which the result data should
                be written. The stream is not automatically closed.
        """
        metrics_json = _SerializableGenerator(
            {
                'key': o.key,
                'description': o.description,
                'unit': o.unit,
                'value_type': o.value_type.__name__,
                'min_value': o.min_value,
                'max_value': o.max_value,
            }
            for o in result.metrics
        )
        subjects_json = _SerializableGenerator(
            {
                'key': o.key,
                'description': o.description,
            }
            for o in result.subjects
        )
        measures_json = _SerializableGenerator(
            {
                'key': o.key,
                'subject': o.subject.key,
                'metric': o.metric.key,
            }
            for o in result.measures
        )
        points_json = _SerializableGenerator(
            {
                'datetime': o.datetime.isoformat(timespec='milliseconds'),
                'values': o.values,
            }
            for o in result.points
        )
        result_json = {
            'identifier': result.identifier,
            'labels': result.labels,
            'meta': result.meta,
            'metrics': metrics_json,
            'subjects': subjects_json,
            'measures': measures_json,
            'points': points_json,
        }
        json.dump(result_json, stream, indent=2)
