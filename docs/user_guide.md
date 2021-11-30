# User guide

This user guide can be used as a starting point for getting a deeper understanding of
the inner workings of the multimeter library. It is meant for users who want to learn
about individual details or who plan to extend its features by developing own
probes or storages.

## Install the library

The library can be installed in two different ways:

### Use stable release from PyPI

All stable versions of multimeter are available on
[PyPI](https://pypi.org/project/multimeter/)
and can be downloaded and installed from there. The easiest option to get it installed
into your python environment is by using `pip`:

```bash
pip install multimeter
```

### Use from source

[Multimeter's Git repository](https://gitlab.com/kantai/multimeter/-/tree/mainline) is
available for everyone and can easily be cloned into a new repository on your local
machine:

```bash
$ cd /your/local/directory
$ git clone https://gitlab.com/kantai/multimeter.git
$ cd multimeter
```

If you want to make changes to library, please follow the guidance in the
[README.md](https://gitlab.com/kantai/multimeter/-/blob/mainline/README.md) on how
to setup the necessary tools for testing your changes.

If you just want to use the library, it is sufficient to add the path to your local
multimeter repository to your `$PYTHONPATH` variable, e.g.:

```bash
$ export PYTHONPATH="$PYTHONPATH:/your/local/directory/multimeter"
```

## How multimeter works

First we start with some high-level description of the individual parts of the library.

### Multimeter

[`Multimeter`](../api/#multimeter.multimeter.Multimeter) is the central class which is
used by the user to start a measurement. A Multimeter takes the configuration, that
defines what and how it is measured. This configuration is usually given directly as
constructor arguments, when instantiating the object:

```python
import multimeter

...

mm = multimeter.Multimeter(
    multimeter.ResourceProbe(),
    cycle_time=5.0,
    storage=multimeter.DummyStorage(),
)
```
Additionally, it can be (re-)configured later:

```python
import multimeter

...

mm = multimeter.Multimeter()

...

mm.add_probes(multimeter.ResourceProbe())
mm.set_cycle_time(5.0)
mm.set_storage(multimeter.DummyStorage())
```


### Probe

For actually capturing the values, `Multimeter` uses an arbitrary number of 
[`Probe`](../api/#multimeter.probe.Probe) objects, which are either provided as
positional arguments in the `Multimeter` constructor or are added after construction
using [`add_probes`](../api/#multimeter.multimeter.Multimeter.add_probes).

Each probe object can define describe values it captures. This is done using 3 different
properties:

##### metrics

[`metrics`](../api/#multimeter.probe.Probe.metrics) contains a tuple of
[`Metric`](../api/#multimeter.metric.Metric) objects, that describe different types of
values that are captured, e.g. the CPU rate spend executing user code or the memory
consumption. A metric can have additional attributes like the python type of the values,
a minimum or maximum value or the unit as string that the value is in. These values are
not checked or enforced in any way, but they can be useful for the interpretation of the
results by the user or other tools.

##### subjects

[`subjects`](../api/#multimeter.probe.Probe.subjects) contains a tuple of
[`Subject`](../api/#multimeter.subject.Subject) objects that describe where a metric
can be captured, e.g. 'process' when capturing the memory usage of a process or a file
system where the free disk space is captured. The supported subjects are `Probe`
dependent, too.

##### measures

The [`measures`](../api/#multimeter.probe.Probe.measures) attribute contains instances
of type [`Measure`](../api/#multimeter.measure.Measure), which references a single
metric and a single subject. The `key` of a `Measure` matches the key under which the
corresponding values are stored.

#### `start()` and `end()`

Probes can implement two methods `start()` and `end()`, which are called when a new
measurement is started or finished. This allows the probe to set up and tear down some
mechanism for collecting the values. Both methods are optional to use and the default
implementations in the `Probe` base class don't do anything.

#### Capturing values

For actually capturing the values, `Probe` subclasses need to implement a method
[`sample(values, time_span)`](../api/#multimeter.probe.Probe.sample). This method is
given a dictionary `values` where the captured values should be added under the key of
their corresponding `Measure`, and a value `time_span` which contains the number of
seconds as `float` since the previous sample or since `start()` in case of the first
call to `sample()`.
The probes are expected to always set a value for each if its `measures`.


Out of the box Multimeter contains the following `Probe` objects:

- [`ResourceProbe`](../probes/resource/)

### Measurement

A new [`Measurement`](../api/#multimeter.measurement.Measurement) is created by
calling the
[`measure()`](../api/#multimeter.multimeter.Multimeter.measure)
method on a `Multimeter` object.

```python
measurement = mm.measure()
```

`measure()` takes optional keyword arguments, that
allows to identify individual measurements later on. If `identifier` is provided, its
value is used as a (unique) identifier for this measurement:

```python
measurement = mm.measure(identfieer='my-measurement')
```

Additionally, arbitrary keyword arguments with string values can be given. Those
are treated as tags that can help to either differentiate between multiple
measurements or contain additional user-defined data:

```python
measurement = mm.measure(
    identfieer='my-measurement',
    my_tag='tag-value',
)
```

#### Measuring

The measurement starts as soon as one calls
[`start()`](../api/#multimeter.measurement.Measurment.start). This starts a new thread
which runs in the background and gathers the measurement values at regular intervals
of length `cycle_time`. This is done until the measurement is ended by calling
[`end()`](../api/#multimeter.measurement.Measurment.end).

```python
measurement.start()
here_my_code_to_be_measured()
...
measurement.end()
```

The [`Result`](../api/#multimeter.result.Result). can be retrieved by explicitly
getting it from the measurement,
```python
result = measurement.result
```
but it's returned from `start()`, too.
```python
result = measurement.start()
```

To make it more convenient the whole `start()`, `end()` sequence is
simplified, when using the `Measurement` as a context manager:

```python
with multimeter.measure() as measurement:
    here_my_code_to_be_measured()
```

#### Adding marks

To make it easier to relate the code that is being measured with the measured values,
a measurement allows adding marks programmatically using the method 
[`add_mark(label)`](../api/#multimeter.measurement.Measurment.add_mark). By calling
this method the current time is saved together with the provided label. This allows to
identify different code sections in a single measurement.

```python
with multimeter.measure() as measurement:
    here_my_code_to_be_measured()
    measurement.add_mark("Next operation")
    next_operation()
    measurement.add_mark("final step")
    final_step()
```

### Result

A [`Result`](../api/#multimeter.result.Result) gives access to the measured values
together with a description of the metrics and the subjects that were captured.

#### points

For each timestamp where values are gathered,
[`point`](../api/#multimeter.result.Result.points) contain an individual object of type
[`Point`](../api/#multimeter.result.Point). Each point contains only two attributes:


1. [`datetime`](../api/#multimeter.result.Point.datetime): A python `datetime.datetime`
  value with timezone UTC that contains the timestamp when the values of the point were
  measured.
2. [`values`](../api/#multimeter.result.Point.values): A `dict()` which contains the
  values for all measures at this time. The types of the individual values depend on
  the `value_type` of the corresponding measure's metric.

#### metrics

[`metrics`](../api/#multimeter.result.Result.metrics) contains the union of all
[`Metric`](../api/#multimeter.metric.Metric) objects defined by all probes that set
the values in this result.

#### subjects

[`subjects`](../api/#multimeter.result.Result.subjects) contain the union of all
[`Subject`](../api/#multimeter.subject.Subject) objects defined by all probes that set
the values in this result.

#### measures

The [`measures`](../api/#multimeter.result.Result.measures) attribute contains
the union of all[`Measure`](../api/#multimeter.measure.Measure), objects defined by
all probes that set the values in this result. The `key` of a `Measure` matches the
key under which the corresponding values are stored.

#### meta_data

All properties in the result are read-only. The only changes to the result by the user
can be made by adding meta data using
[`Result.add_meta_data(**meta_data)`](../api/#multimeter.result.Result.add_meta_data).
The meta data values can be strings or other primitives. It is meant for storing
additional information about the run, that can be useful for interpreting the result,
e.g. instance type, operating system version, user account who executes the code etc.

### Storage

Once a measurement is finished, its result can be automatically stored by a
[`Storage`](../api/#multimeter.storages.base.Storage). `Storage` classes need to
implement only a single method: [`store(result)`](../api/#multimeter.storages.base.Storage.store)
This method takes as only argument the `Result` of the measurement.

Multimeter provides the following different `Storage` implementations:

- [`JsonFileStorage`](../storages/jsonfile/)

## Extending multimeter

Multimeter can easily be extended on two sides, gathering values and storing values.

### Implementing custom probe

A new probe should inherit from the [`Probe`](../api/#multimeter.probe.Probe) base class.
The only method that needs to be implemented is `sample(values, time_span`.

In order to make
it easier to understand, what different measures, subjects and metrics the new probe uses,
the corresponding methods [`measures`](../api/#multimeter.probe.Probe.measures),
[`subjects`](../api/#multimeter.probe.Probe.subjects) and
[`metrics`](../api/#multimeter.probe.Probe.metrics) should be implemented and match, the
values, that `sample(values, time_span)` defines. If applicable, some predefined metrics
`METRIC_*` in `multimeter.metrics` and subjects `SUBJECT_*` in `multimeter.subjects` can be
used.

`start()` and `end()` can be implemented if useful for initialization or cleaning up.

### Implementing custom storage

Implementing a custom storage class is quite easy. Inherit from the base class
[`multimeter.storages.base.Storage`](../api/#multimeter.storages.base.Storage) and implement
the method [`store(result)`](../api/#multimeter.storages.base.Storage.store).
