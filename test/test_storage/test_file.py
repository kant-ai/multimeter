import datetime
import json
import pathlib
import shutil
import tempfile
import unittest

from multimeter.result import Result
from multimeter.storages.file import FileFormat, FileStorage, JsonFormat, LineFormat


class DummyFormat(FileFormat):

    @property
    def extension(self):
        return '.dummy'

    def save_result_to_stream(self, result, stream):
        stream.write(b'result')


class TestFileStorage(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.storage = FileStorage(pathlib.Path(self.dir), DummyFormat())

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_directory_is_wrapped_with_path(self):
        storage = FileStorage(self.dir, DummyFormat())
        self.assertIsInstance(storage.save_directory, pathlib.Path)

    def test_storage_requires_directory(self):
        with self.assertRaisesRegex(ValueError, "'save_directory' must be set"):
            FileStorage(None, DummyFormat())

    def test_save_directory_is_created_when_first_result_is_stored(self):
        save_dir = pathlib.Path(self.dir)
        save_dir.rmdir()
        storage = FileStorage(save_dir, DummyFormat())

        self.assertFalse(save_dir.exists())

        result = Result(identifier='result')
        storage.store(result)

        self.assertTrue(save_dir.exists())

    def test_result_is_saved_in_single_file_with_correct_name_and_content(self):
        result = Result(identifier='result')
        self.storage.store(result)

        result_file_path = pathlib.Path(self.dir) / 'result.dummy'
        self.assertTrue(result_file_path.exists())
        self.assertTrue(result_file_path.is_file())
        self.assertEqual(b'result', result_file_path.read_bytes())


class TestJsonFormat(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.storage = FileStorage(pathlib.Path(self.dir), JsonFormat())

    def test_result_can_be_saved_as_json(self):
        result = Result(identifier='result')
        result.append(datetime.datetime(2021, 1, 1, 1, 1), {})
        result.append(datetime.datetime(2021, 1, 1, 1, 10), {})

        self.storage.store(result)
        with open(self.dir+f'/result.json', 'r') as stream:
            json_obj = json.load(stream)

        ref = {
            'identifier': 'result',
            'tags': {},
            'meta_data': {},
            'schema': {
                'metrics': [],
                'subjects': [],
                'measures': [],
            },
            'points': [
                {"datetime": "2021-01-01T01:01:00.000", "values": {}},
                {"datetime": "2021-01-01T01:10:00.000", "values": {}},
            ],
            'marks': [],
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
            'tags': {},
            'meta_data': {},
            'schema': {
                'metrics': [],
                'subjects': [],
                'measures': [],
            },
            'points': [
                {"datetime": "2021-01-01T01:01:00.000", "values": {"a": 1}},
            ],
            'marks': [],
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
            'tags': {},
            'meta_data': {'data': 'values', 'my': 'meta'},
            'schema': {
                'metrics': [],
                'subjects': [],
                'measures': [],
            },
            'points': [],
            'marks': [],
        }
        self.assertEqual(ref, json_obj)


class TestLineFormat(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.storage = FileStorage(pathlib.Path(self.dir), LineFormat())

    def test_invalid_identifier(self):
        result = Result(identifier='_underscore_')
        with self.assertRaisesRegex(ValueError, "Identifier can't start with '_'"):
            self.storage.store(result)

        result = Result(identifier='')
        with self.assertRaisesRegex(ValueError, "Identifier can't be empty."):
            self.storage.store(result)

        result = Result(identifier='multi\nline')
        with self.assertRaisesRegex(ValueError, "Identifier can't contain line breaks."):
            self.storage.store(result)

    def test_multiple_lines_for_multiple_points(self):
        result = Result(identifier='result')
        result.append(
            datetime.datetime(
                2021, 1, 1, 1, 1, 2, 345678, tzinfo=datetime.timezone.utc,
            ),
            {'a': 1},
        )
        result.append(
            datetime.datetime(
                2021, 1, 1, 1, 1, 3, 345678, tzinfo=datetime.timezone.utc,
            ),
            {'a': 2},
        )
        result.append(
            datetime.datetime(
                2021, 1, 1, 1, 1, 4, 345678, tzinfo=datetime.timezone.utc,
            ),
            {'a': 3},
        )

        self.storage.store(result)
        with open(self.dir+f'/result.line', 'r') as stream:
            line = stream.readline().strip()
            self.assertEqual(
                'result a=1i 1609462862345678080',
                line,
            )
            line = stream.readline().strip()
            self.assertEqual(
                'result a=2i 1609462863345678080',
                line,
            )
            line = stream.readline().strip()
            self.assertEqual(
                'result a=3i 1609462864345678080',
                line,
            )

    def test_identifier_is_correctly_escaped(self):
        result = Result(identifier='with space and,comma')
        result.append(
            datetime.datetime(
                2021, 1, 1, 1, 1, 2, 345678, tzinfo=datetime.timezone.utc,
            ),
            {'a': 1},
        )

        self.storage.store(result)
        with open(self.dir+f'/with space and,comma.line', 'r') as stream:
            line = stream.readline().strip()
            self.assertEqual(
                r'with\ space\ and\,comma a=1i 1609462862345678080',
                line,
            )

    def test_keys_are_correctly_escaped(self):
        result = Result(identifier='result')
        result.append(
            datetime.datetime(
                2021, 1, 1, 1, 1, 2, 345678, tzinfo=datetime.timezone.utc,
            ),
            {'with,comma': 1, 'with=equal': 2, 'with space': 3},
        )

        self.storage.store(result)
        with open(self.dir+f'/result.line', 'r') as stream:
            line = stream.readline().strip()
            self.assertEqual(
                r'result with\,comma=1i,with\=equal=2i,with\ space=3i 1609462862345678080',
                line,
            )

    def test_values_are_correctly_formatted(self):
        result = Result(identifier='result')
        result.append(
            datetime.datetime(
                2021, 1, 1, 1, 1, 2, 345678, tzinfo=datetime.timezone.utc,
            ),
            {'a': 1, 'b': 1.0, 'c': True, 'd': False, 'e': 'String'},
        )

        self.storage.store(result)
        with open(self.dir+f'/result.line', 'r') as stream:
            line = stream.readline().strip()
            self.assertEqual(
                'result a=1i,b=1.0,c=True,d=False,e="String" 1609462862345678080',
                line,
            )

    def test_string_values_are_correctly_escaped(self):
        result = Result(identifier='result')
        result.append(
            datetime.datetime(
                2021, 1, 1, 1, 1, 2, 345678, tzinfo=datetime.timezone.utc,
            ),
            {'a': 'String with space', 'b': r"with\backslash", 'c': 'with"quotes'},
        )

        self.storage.store(result)
        with open(self.dir+f'/result.line', 'r') as stream:
            line = stream.readline().strip()
            self.assertEqual(
                r'result a="String with space",b="with\\backslash",c="with\"quotes" 1609462862345678080',
                line,
            )

    def test_tags_are_correctly_formatted(self):
        result = Result(identifier='result', tags={'my': 'tag', 'with': 'label'})
        result.append(
            datetime.datetime(
                2021, 1, 1, 1, 1, 2, 345678, tzinfo=datetime.timezone.utc,
            ),
            {'a': 1},
        )

        self.storage.store(result)
        with open(self.dir+f'/result.line', 'r') as stream:
            line = stream.readline().strip()
            self.assertEqual(
                'result,my=tag,with=label a=1i 1609462862345678080',
                line,
            )

    def test_tags_are_correctly_escaped(self):
        result = Result(identifier='result', tags={
            'with,comma': 'a,value',
            'with=equal': 'a=value',
            'with space': 'a value',
        })
        result.append(
            datetime.datetime(
                2021, 1, 1, 1, 1, 2, 345678, tzinfo=datetime.timezone.utc,
            ),
            {'a': 1},
        )

        self.storage.store(result)
        with open(self.dir+f'/result.line', 'r') as stream:
            line = stream.readline().strip()
            self.assertEqual(
                r'result,with\,comma=a\,value,with\=equal=a\=value,with\ space=a\ value a=1i 1609462862345678080',
                line,
            )


if __name__ == '__main__':
    unittest.main()
