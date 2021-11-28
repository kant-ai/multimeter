
# FAQ

## What is the difference between python profilers like cProfile and multimeter?

Profilers typically measure how the code behaves internally, e.g. which function was
called most and took the longest time to run or where most of the memory was allocated.
Profiling code in detail is costly and is therefore only done explicitly when one is
trying to optimize some specific behavior.
Multimeter in contrast doesn't care of the internals of code, but looks at the external
effects of this code like cpu load, overall memory consumption or amount of io. This
is comparatively cheap and can easily show potential bottlenecks.

So, in short, multimeter allows identifying code that could have optimization potential
and should be run using a profiler.

## Why do I get the warning "Sampling lagging behind cycle time, ignore sleep"?

Usually the background thread waits until the measures are sampled next. If the
sampling of all metrics takes longer than the cycle time, this warning is written to
the log to indicate that the cycle time is too short for accurate measuring. The
easiest fix for repeated warnings is increasing the cycle time.
