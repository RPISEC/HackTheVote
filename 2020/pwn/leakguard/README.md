# A writeup of sorts

## Overview

This challenge is a standard menu binary themed around a candle shop. You can make wax,
get rid of wax, pour a candle from existing wax, and sell poured candles.

The waxes are managed with reference counting: using a wax to pour a candle will increment
its refcount, selling that candle will decrement it. The refcount is an unsigned char.

The binary executes with `LD_PRELOAD=leakguard.so`, which redefines the `write`
function, and hooks libc's `write` function to jump into the alternate. As the shared
object's name suggests, this new `write` function attempts to prevent info leaks.

It first parses `/proc/self/maps` to determine currently mapped memory regions. It then
iterates through the buffer, and interprets every sequence of 1 to 8 bytes as a potential
address. If any of these match up with a mapped region, the leak is redacted by memsetting
that part of the buffer to 0.

## Bug

Newly poured candles can be given a name, however the name is not null-terminated after
being read in. The immediately adjacent struct member is a reference to the wax used to
pour the candle. When printing the candle's name, leakguard will detect the leak and
null out this pointer. Consequently, the reference is lost, and selling the candle
doesn't decrement the refcount. The refcount being an unsigned char, it is quite
practical to overflow.

Due to constraints on the number of candles that can be poured, this overflow would not
be possible without our good friend leakguard.

We can use this overflow to UAF a wax.

## Pwn

Bypassing the leak protection isn't all that difficult. First we'll want
a partial leak to start with. By creating some tcache entries, and then allocating
a candle, the first 8 uninitialized bytes will be a heap pointer (part of the tcache list).
By overwriting the first 2 bytes with 0x0101, we can make this an invalid address
(with high enough probability for a ctf solution) and therefore leak the top
6 bytes of the heap base.

Now we just need the one nibble. We use leakguard as an oracle: if we make the candle's
name contain a valid address, it gets nulled, otherwise it's an invalid address. We
can then binary search for the base of the heap.

The UAF of the wax can give us arbitrary control of a wax struct, which contains
some `char*`s. To obtain a text leak, and subsequently a libc leak,
we can simply point a `char*` at `&ptr_we_want_to_leak + 1`
(there are text pointers on the heap, and libc pointers in the got).

Armed with a libc leak and the UAF, we double free a tcache entry (it's ubuntu 18
libc 2.27, so no tcache double free detection) and overwrite `__free_hook`.
