# Getting started

## Install the library

Install the latest version from [PyPI](https://pypi.org/project/multimeter/)
using pip:

```bash
pip install multimeter
```

## Create a multimeter in your code

Create a new instance of `Multimeter` with the probes it should use:

```python
import multimeter

...

mm = multimeter.Multimeter(multimeter.ResourceProbe())
```

## Measure while executing the code you want to measure

```python
with mm.measure(identifier='measurement-id') as measurement:
    # Here the code whose performance should be measured
    ...
```

## Process the measured results

```python
print(f"Start {measurement.result.start}")
print(f"End {measurement.result.end}")
print(f"Duration {measurement.result.duration}")
print(f"CPU avg values: {measurement.result.values('process.cpu_rate_user')}")
```

## Automatically store the results as JSON

```python
mm.set_storage(multimeter.JsonFileStorage(save_directory='/my/directory'))
```

## Where to go from here?

Read the [user guide](../user_guide/) for some more in-depth explanation about multimeter.

Multimeter supports different types of probes, that actually measure. A description of
the individual classes with their respective metrics can be found in the documentation:

- Which metrics are available?
    [`multimeter.probe.ResourceProbe`](../probes/resource/)
- Where can I store the results?
    [`multimeter.storage.JsonFileStorage`](../storages/jsonfile/)
- Creating your own probe:
    [How to write your own probe?](../user_guide/#implementing-custom-probe)
- Creating your own storage:
    [How to write your own probe?](../user_guide/#implementing-custom-storage)
