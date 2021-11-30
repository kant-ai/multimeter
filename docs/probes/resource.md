# ResourceProbe

The [`multimeter.probe.ResourceProbe`](../../api/#multimeter.probe.ResourceProbe)
uses the python standard module `resource` that provides access to cpu load, memory
usage and io metrics. Unfortunately, the module is only available on unix.

## Metrics
- METRIC_CPU_RATE_USER: Rate of time spent in user side code per second
- METRIC_CPU_RATE_SYSTEM: Rate of time spent in user side code per second
- METRIC_MEMORY_MAX: Total memory allocated in kB.
- METRIC_MEMORY_SHARED: Shared memory with other processes in kB.
- METRIC_MEMORY_DATA: Memory used for data in kB.
- METRIC_MEMORY_STACK: Memory used for stacks in kB.
- METRIC_MEMORY_PAGE_FAULTS_WITH_IO: Number of page faults per second that lead to io.
- METRIC_MEMORY_PAGE_FAULTS_WITHOUT_IO: Number of page faults per second that didn't lead to io.
- METRIC_MEMORY_SWAP_OPS: Number of swap operations per second.
- METRIC_IO_BLOCK_IN: Number of data blocks read per second.
- METRIC_IO_BLOCK_OUT: Number of data blocks writes per second.
- METRIC_CONTEXT_SWITCHES_VOL: Number of voluntary context switches per seconds.
- METRIC_CONTEXT_SWITCHES_INVOL: Number of involuntary context switches per seconds.

See [https://man7.org/linux/man-pages/man2/getrusage.2.html](https://man7.org/linux/man-pages/man2/getrusage.2.html) for more details.

## Subjects
- SUBJECT_PROCESS: The python process.
- SUBJECT_CHILDREN: The child processes of the python process.
