# InfluxDBStorage

The [`multimeter.storages.influx.InfluxDBStorage`](../../api/#multimeter.storages.influx.InfluxDBStorage)
exports all `Result` to an Influx time series database.

`InfluxDBStorage` uses the official [`influxdb_client`](https://github.com/influxdata/influxdb-client-python)
library and therefore, depends on its package to be installed. It can be automatically
installed alongside `multimeter` by installing its optional extra `[influxdb]`:

```bash
pip install multimeter[influxdb]
```

## Configuration

All configuration values are given as arguments to the
[InfluxDBStorage constructor `__init__()`](../../api/#multimeter.storages.influx.InfluxDBStorage.__init__())
`token` is required and given as a positional argument, where all other values of the
configuration are optional keyword values.

### token
The `InfluxDBStorage` requires an authentication `token` to be able to write data to
the database. This token can be manually created in the InfluxDB user interface or in
an automated fashion using InfluxDB clients.

### url
The `url` value defines the URL of the InfluxDB server instance to which the data will
be sent. The `url` can be left out in which case, the URL of a server running on
localhost with the default port is being use: 'http://localhost:8086'

### org
Every data in an InfluxDB is assigned to be owned by an organization. The
organizations are defined by the InfluxDB server and can be managed using its UI.
As a default multimeter uses an organization 'kantai', but if this organization is
not defined, InfluxDB will send an error 'organization name \"kantai\" not found'.

### bucket
In InfluxDB data can be stored in different buckets. The name of the `bucket` can be
specified as part of the configuration. If no value is given for `bucket`, multimeter
expects a bucket with name `multimeter`.


## Example

```python
from multimeter import Multimeter, ResourceProbe
from multimeter.storages.influx import InfluxDBStorage

meter = Multimeter(ResourceProbe(), storage=InfluxDBStorage(
    'IWWNNY1xWuyxKCoc_KiucH-u9E6hqeXFXzi49sKzQY5VhZgdwqbrMJCF_z7xQocd_20xuuH1kMNgRnPzrvmIOA==',
    url='http://influxdb2.my.tld:8086', org='my-org', bucket='my-bucket',
))
```