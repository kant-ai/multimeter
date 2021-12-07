"""Store measurements in an InfluxDB"""
import logging

import influxdb_client

from multimeter.storages.base import Storage


logger = logging.getLogger(__name__)


class InfluxDBStorage(Storage):
    """
    Storage implementation that stores results in InfluxDB.

    The identifier of the result is used as the "measurement". The results from the
    measured are mapped to InfluxDB fields and tags are supported as well. The
    constructor of the storage allows to configure, under which org and in which
    bucket the data will be stored. Which InfluxDB to use is configured by the `url`
    argument, authorization is done using an authorization token, that has to be
    generated from the InfluxDB server.
    """

    def __init__(
        self,
        token,
        url="http://localhost:8086",
        org="kantai",
        bucket="multimeter",
    ):
        """
        Creates a new InfluxDB storage.

        Args:
            token (str): The authentication token for InfluxDB.
            url (url): The URL to the InfluxDB instance. Defaults to
                'http://localhost:8086'.
            org (str): The id of the organization which should own the data. Defaults
                to 'kantai'.
            bucket (str): The bucket where the data will be stored. Defaults to
                'multimeter'.
        """
        if token is None:
            raise ValueError("'token' must be set.")
        self._bucket = bucket
        self._client = influxdb_client.InfluxDBClient(url, token, org=org)
        logger.info("Created influxdb client with url '%s', org '%s'.", url, org)

    def store(self, result):
        def create_influxdb_point(identifier, point):
            influx_point = influxdb_client.Point(identifier).time(point.datetime)
            for field, value in point.values.items():
                influx_point.field(field, value)
            return influx_point

        point_settings = influxdb_client.client.write_api.PointSettings()
        for label, value in result.tags.items():
            point_settings.add_default_tag(label, value)

        write_client = self._client.write_api(
            write_options=influxdb_client.client.write_api.SYNCHRONOUS,
            point_settings=point_settings,
        )

        records = (
            create_influxdb_point(result.identifier, point) for point in result.points
        )
        logger.info("Write new measurement %s to data base", result.identifier)
        write_client.write(bucket=self._bucket, record=records)
