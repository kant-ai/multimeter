import datetime
import unittest.mock

from multimeter.result import Result
from multimeter.storages.influx import InfluxDBStorage


class TestInfluxDBStorage(unittest.TestCase):

    def test_constructor_requires_token(self):
        with self.assertRaisesRegex(ValueError, "'token' must be set"):
            InfluxDBStorage(None)

    def test_arguments_are_given_to_client(self):
        with unittest.mock.patch('influxdb_client.InfluxDBClient') as client_mock:
            InfluxDBStorage('my-token', url='http://my/url', org='my-org')
        client_mock.assert_called_with('http://my/url', 'my-token', org='my-org')

    def test_write_client_is_created_with_tags(self):
        result = Result(tags={'my': 'tag', 'other': 'value'})

        with unittest.mock.patch('influxdb_client.InfluxDBClient.write_api') as write_mock:
            storage = InfluxDBStorage('my-token')
            storage.store(result)

        self.assertEqual({'my': 'tag', 'other': 'value'}, write_mock.call_args[1]['point_settings'].defaultTags)

    def test_all_points_are_written_to_the_correct_bucket(self):
        result = Result()
        result.append(datetime.datetime(2021, 12, 1, 1, 1, 1), {'a': 1, 'b': '2'})
        result.append(datetime.datetime(2021, 12, 1, 1, 1, 2), {'a': 3, 'b': '4'})

        with unittest.mock.patch('influxdb_client.InfluxDBClient.write_api') as write_api_mock:
            storage = InfluxDBStorage('my-token', bucket='my-bucket')
            storage.store(result)

        write_method_mock = write_api_mock.return_value.write
        self.assertEqual('my-bucket', write_method_mock.call_args[1]['bucket'])
        records = list(write_method_mock.call_args[1]['record'])
        self.assertEqual(2, len(records))
        self.assertEqual(datetime.datetime(2021, 12, 1, 1, 1, 1), records[0]._time)
        self.assertEqual({'a': 1, 'b': '2'}, records[0]._fields)
        self.assertEqual(datetime.datetime(2021, 12, 1, 1, 1, 2), records[1]._time)
        self.assertEqual({'a': 3, 'b': '4'}, records[1]._fields)



if __name__ == '__main__':
    unittest.main()
