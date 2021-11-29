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
are treated as labels that can help to either differentiate between multiple
measurements or contain additional user-defined data:

```python
measurement = mm.measure(
    identfieer='my-measurement',
    my_label='label-value',
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

### Result

A [`Result`](../api/#multimeter.result.Result) gives access to the measured values
together with a description of the metrics and the subjects that were captured.


### Storage

### Probe


#### Metric

#### Subject

#### Measure


## Extending multimeter

### Implementing custom probe

### Implementing custom storage
