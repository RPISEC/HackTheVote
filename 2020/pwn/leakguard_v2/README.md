# A writeup of sorts

## Overview

The main executable is exactly the same as for the original challenge. The leakguard
library has a slight change: before checking for leaks, it aligns the start of the buffer
on an 8 byte boundary, and aligns the size as well (rounding up). This means we can't
use the +1 trick to obtain leaks.

The challenge is also now running on ubuntu 20 with libc 2.31, meaning double free
tcache checks are now a concern.

## Pwn

The inital heap leak can be done exactly the same way.

Getting a text leak can be done in a similar fashion, although we need
to use a linear search instead (since the size of the binary's mapped
sections isn't large enough to cover the min/max for binary search).

We can still obtain a double free, again thanks to our good friend leakguard.
If we point some `char*` at a tcache chunks key, we can null it out, therefore
bypassing the double free detection.

With the double free, we can redirect the tcache list to point at the `stdout` pointer
in the data section. If we then consume a few tcache entries, we'll have `stdout`
as the head of the tcache. One thing to note however, is that in doing this,
we will have allocated a candle pointing at the `stdout` pointer in the data section,
and printing this candle will null it out, causing a segfault the next time we
try to print anything. We can carefully work around this by pointing a `char*` into
the array of candles where this problematic candle will end up, and using leakguard
to null it out.

With `stdout` as the head of the tcache, we can perform the same binary search technique
as before to leak the mmap base and libc.

Then we do another double free, and overwrite `__free_hook`

That's the basic idea, implementation details are left as an exercise
for the determined reader.
