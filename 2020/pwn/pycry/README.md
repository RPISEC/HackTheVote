# A writeup of sorts

## Overview

The point of this challenge is to exploit a bug in pycrypto and pwn the python2 interpreter.
This bug was discovered completely by accident.
note that pycrypto is very end of life and unmaintained, just like python2, very sad...

The challenge lets you give arbitrary inputs to the `isPrime` function provided
by pycrypto, which should've acted as a clear indication of where to look.

## Bug

The inputs to `isPrime` are described in the docstring:
```
    isPrime(N:long, false_positive_prob:float, randfunc:callable):bool
    Return true if N is prime.

    The optional false_positive_prob is the statistical probability
    that true is returned even though it is not (pseudo-prime).
    It defaults to 1e-6 (less than 1:1000000).
    Note that the real probability of a false-positive is far less. This is
    just the mathematically provable limit.

    If randfunc is omitted, then Random.new().read is used.
```
The challenge sets up randfunc so that it returns a user-supplied
sequence of strings.

A little digging will show that `isPrime` calls out to a function of the same name
in the `_fastmath` library, defined
[here](https://github.com/pycrypto/pycrypto/blob/master/src/_fastmath.c#L968).
This function ends up calling `rabinMillerTest`, defined
[here](https://github.com/pycrypto/pycrypto/blob/master/src/_fastmath.c#L1248).

Here are some relevant code snippets:
```c
static PyObject *
isPrime (PyObject * self, PyObject * args, PyObject * kwargs)
{
    unsigned int rounds;
    ...
    rounds = (unsigned int)ceil (-log (false_positive_prob) / log (4));
    result = rabinMillerTest(n, rounds, randfunc);
    ...
}

static int
rabinMillerTest (mpz_t n, int rounds, PyObject *randfunc)
{
    mpz_t a;
    mpz_t tested[MAX_RABIN_MILLER_ROUNDS];

    if (rounds > MAX_RABIN_MILLER_ROUNDS) // [1]
    {
        PyErr_Warn(PyExc_RuntimeWarning,
                      "rounds to Rabin-Miller-Test exceeds maximum. "
                      "rounds will be set to the maximum.\n"
                      "Go complain to the devs about it if you like.");
        rounds = MAX_RABIN_MILLER_ROUNDS;
    }
    
    ...

    for (i = 0; i < (unsigned long)rounds; ++i) // [2]
    {
        // populate 'a' from randfunc
        ...

        mpz_init_set (tested[i], a);

        ...
    }

    ...
}
```

The argument `rounds` to `rabinMillerTest` is an `int`, and therefore
the comparison at `[1]` is signed. At `[2]` however, `rounds` is explicitly
casted to an `unsigned long`, meaning the comparison is unsigned.

If we can have `rounds` be negative (which is easily achieved if
`log(false_positive_prob)` is positive) then the loop can execute
way more times than expected. On each loop iteration,
it initializes an `mpz_t` in the `tested` array, giving us some sort of stack overflow.

Some practical concerns: pycrypto was compiled without stack canaries; we can
break out of the loop if `randfunc` runs out of values.

## Pwn

We'll need a bit more understanding before getting a useful primitive. The array
that we can overflow (`tested`) is an array of `mpz_t` structures, which are defined
[here](https://fossies.org/dox/gmp-6.2.0/mini-gmp_8h_source.html#l00067):
```c
typedef struct
{
  int _mp_alloc;        /* Number of *limbs* allocated and pointed
                   to by the _mp_d field.  */
  int _mp_size;         /* abs(_mp_size) is the number of limbs the
                   last field points to.  If _mp_size is
                   negative this is a negative number.  */
  mp_limb_t *_mp_d;     /* Pointer to the limbs.  */
} __mpz_struct;

typedef __mpz_struct mpz_t[1];
```

The first two fields are sizes, and `_mp_d` is just a pointer to the raw bytes
representing the integer's value.

The raw bytes are fully under our control, they are obtained from randfunc. This gives
us a primitive of corrupting something on the stack with a pointer to controlled data.

Overwriting the return address with a pointer to our controlled data isnt an option with
NX. However if we look at some of the callee-saved registers on the stack,
we'll see that on returning from `rabinMillerTest`, one of them is passed directly
to `mpz_clear`, which takes a pointer to an `mpz_t`. This means our controlled
data will be interpreted as the `mpz_t` struct.

`mpz_clear` is essentially: `free(mpz->_mp_d)`. We now have an arbitrary free, after
which the process will continue as normal (meaning we can trigger this primitive
over and over).

The python interpreter was compiled without pie, so we can look for potential targets
to free in the binary's data section.
We'll need `free` to succeed of course, so the memory we free must look
like a valid heap chunk. The challenge is running on ubuntu 18, so tcache is also
there to make things a bit easier. The fake chunk must then meet the following
criteria:
- properly aligned at 16 byte boundary
- mmap bit unset (bit 1)
- non_main_arena bit unset (bit 2)
- size must be aligned to 16 bytes (cant have bit 3 set)
- size must be >= 0x10
- size must be <= 0x420 for tcache

I couldn't manage to find any such chunks in range of an interesting target,
so instead we can adopt a multi-step approach:
- free some fake chunk before the corruption target
- reclaim it and place a fake chunk header at the end
- free this new fake chunk
- repeat until you reach the target

The solution included here targets some internal python struct containing a vtable,
triggering an arbitrary function call where the first arg is the struct itself
(similar to glibc FILE struct vtable calls), which it leverages
to call `system("sh")`
