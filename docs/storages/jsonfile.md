# JsonFileStorage

The [`multimeter.storages.json.JsonFileStorage`](../../api/#multimeter.storages.json.JsonFileStorage)
exports all `Result` to the file system using JSON.

## Configuration

The only configuration that
[`multimeter.storages.json.JsonFileStorage.__init__`](../../api/#multimeter.storages.json.JsonFileStorage.__init__)
takes is a path to a directory, where the JSON files will be stored.

## Format

The json structure is a single object with fixed attributes:

```json
{
  "identifier": "measure-id",
  "tags": {
    "tag": "value"
  },
  "meta_data": {},
  "schema": {
    "metrics": [
      {
        "key": "cpu_rate_user",
        "description": "The rate of the time where the CPU is executing user-space code.",
        "unit": "",
        "value_type": "float",
        "min_value": 0.0,
        "max_value": 1.0
      },
      {
        "key": "cpu_rate_system",
        "description": "The rate of the time where the CPU is executing system code.",
        "unit": "",
        "value_type": "float",
        "min_value": 0.0,
        "max_value": 1.0
      }
    ],
    "subjects": [
      {
        "key": "process",
        "description": "The current running process."
      }
    ],
    "measures": [
      {
        "key": "process.cpu_rate_user",
        "subject": "process",
        "metric": "cpu_rate_user"
      },
      {
        "key": "process.cpu_rate_system",
        "subject": "process",
        "metric": "cpu_rate_system"
      }
    ]
  },
  "points": [
    {
      "datetime": "2021-11-27T18:43:51.033+00:00",
      "values": {
        "process.cpu_rate_user": 0.8287030088703983,
        "process.cpu_rate_system": 0.2367722882486841
      }
    },
    {
      "datetime": "2021-11-27T18:43:52.039+00:00",
      "values": {
        "process.cpu_rate_user": 1.0000167626132233,
        "process.cpu_rate_system": 5.469854836835e-05
      }
    }
  ],
  "marks": [
    {
      "datetime": "2021-11-27T18:43:51.733+00:00",
      "label": "Call X"
    }
  ]
}
```

### identifier

The identifier for the measurement, which created this result.

### tags

Tags are user-defined when the measurement is created.

### meta_data

Contains the meta data that can be added to the result using `add_meta_data()`.

### schema

The schema contains a description of the different values that are measured.
Their definition originates the metrics, subjects and measures:

#### metrics

A list of objects describing the metrics that are included in the results. Each object
contains the attributes "key", "description", "unit", "value_type", "min_value" and
"max_value".

#### subjects

A list of objects where each object represents a subject from which the metrics were
sampled. Each object contains a "key" and a human-readable "description".

#### measure

A list of objects representing individual measures describing which metric was sampled
for which subject. Each object contains a "key" and references to a "subject" and a
"metric".

### points

The list of individual measuring points. Each point has an attribute "datetime"
containing the datetime (UTC) the values were measured and an attribute "values"
with a javascript object, where the keys reference the measures and the values
contain the measured values at this time.

### marks

The list of timestamps with a mark. Each mark has an attribute "datetime"
containing the datetime (UTC) and an attribute "label" which contains the
label of the mark, that was given when the mark was made.
