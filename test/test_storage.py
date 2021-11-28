import datetime
import json
import pathlib
import shutil
import tempfile
import unittest

from multimeter.storage import JsonFileStorage
from multimeter.result import Result


class TestJsonFileStorage(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.storage = JsonFileStorage(pathlib.Path(self.dir))

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_directory_is_wrapped_with_path(self):
        storage = JsonFileStorage(self.dir)
        self.assertIsInstance(storage.save_directory, pathlib.Path)

    def test_storage_requires_directory(self):
        with self.assertRaisesRegex(ValueError, "'save_directory' must be set"):
            JsonFileStorage(None)

    def test_result_can_be_saved_as_json(self):
        result = Result(identifier='result')
        result.append(datetime.datetime(2021, 1, 1, 1, 1), {})
        result.append(datetime.datetime(2021, 1, 1, 1, 10), {})

        self.storage.store(result)
        with open(self.dir+f'/result.json', 'r') as stream:
            json_obj = json.load(stream)

        ref = {
            'identifier': 'result',
            'labels': {},
            'measures': [],
            'meta': {},
            'metrics': [],
            'subjects': [],
            'points': [
                {"datetime": "2021-01-01T01:01:00.000", "values": {}},
                {"datetime": "2021-01-01T01:10:00.000", "values": {}},
            ]
        }
        self.assertEqual(ref, json_obj)

    def test_result_can_be_saved_with_data(self):
        result = Result(identifier='result')
        result.append(datetime.datetime(2021, 1, 1, 1, 1), {'a': 1})

        self.storage.store(result)
        with open(self.dir+f'/result.json', 'r') as stream:
            json_obj = json.load(stream)

        ref = {
            'identifier': 'result',
            'labels': {},
            'measures': [],
            'meta': {},
            'metrics': [],
            'subjects': [],
            'points': [
                {"datetime": "2021-01-01T01:01:00.000", "values": {"a": 1}},
            ]
        }
        self.assertEqual(ref, json_obj)

    def test_saved_result_contains_meta_data(self):
        result = Result(identifier='result')
        result.add_meta_data(my='meta', data='values')

        self.storage.store(result)
        with open(self.dir+f'/result.json', 'r') as stream:
            json_obj = json.load(stream)

        ref = {
            'identifier': 'result',
            'labels': {},
            'measures': [],
            'meta': {'data': 'values', 'my': 'meta'},
            'metrics': [],
            'subjects': [],
            'points': [],
        }
        self.assertEqual(ref, json_obj)


if __name__ == '__main__':
    unittest.main()
