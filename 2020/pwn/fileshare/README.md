# A writeup of sorts

If any determined hackers are trying to figure this out on their own,
but have given up, perhaps these hints will help reinspire:
- for the bug: `strace cat .`
- for how to use it: strace pthread creation, obscure syscalls may be worth investigating

## Overview

A wrapper binary is executed as root before spawning the main challenge binary.
It creates a temp directory and copies the flag file, challenge binary, and
some libraries into the new dir
(note that the flag filename is of the form `flag-[random unknown hash]`).
It then executes the `unshare` userspace utility, passing args to run the challenge
binary in the following environment:
- in a new pid namespace
- with procfs mounted
- chroot'd into the temp dir
- working dir `/files` under the chroot

The challenge binary then performs the following setup code:
- drops privs to `nobody:nogroup`
- creates a socket listening on a randomly assigned port, notifying the user of the port
- enters a handling loop

When a client connects to this new port, a new thread is created to handle the connection.
Each thread is under a seccomp sandbox, and communicates with the main thread
to perform some basic file operations (upload/download). For completeness,
here is the sandbox, dumped with the very useful
[seccomp-tools](https://github.com/david942j/seccomp-tools):
```
 line  CODE  JT   JF      K
=================================
 0000: 0x20 0x00 0x00 0x00000004  A = arch
 0001: 0x15 0x00 0x07 0xc000003e  if (A != ARCH_X86_64) goto 0009
 0002: 0x20 0x00 0x00 0x00000000  A = sys_number
 0003: 0x15 0x06 0x00 0x00000000  if (A == read) goto 0010
 0004: 0x15 0x05 0x00 0x00000001  if (A == write) goto 0010
 0005: 0x15 0x04 0x00 0x0000003c  if (A == exit) goto 0010
 0006: 0x15 0x00 0x02 0x00000009  if (A != mmap) goto 0009
 0007: 0x20 0x00 0x00 0x00000010  A = addr # mmap(addr, len, prot, flags, fd, pgoff)
 0008: 0x15 0x01 0x00 0x00000000  if (A == 0x0) goto 0010
 0009: 0x06 0x00 0x00 0x00000000  return KILL
 0010: 0x06 0x00 0x00 0x7fff0000  return ALLOW
```

The main thread keeps track of each client thread in an array of ipc structs,
which includes an unsigned char indicating the client's state: whether it is free
(meaning this slot in the array is unused), dead (waiting to be cleaned up), idle,
or currently requesting an upload/download. On a new connection, the main thread
uses a free slot in this array and creates the new thread. Threads are created
with a user-defined stack that has guard pages on both ends (as opposed to
having `pthread_create` automatically allocate a stack, which will have only
one guard page on the lower-address end). On start, each thread sets a signal handler
for `SIGSEGV` and `SIGPIPE` that simply does a `SYS_exit` syscall (this will
only terminate the calling thread, as opposed to `SYS_exit_group` which kills
the whole proc).

Occasionally (at least once a second) the main thread will iterate through all clients
and process any that died, cleaning up any resources allocated for the thread.

Clients can either upload or download files, each with a "secure" variant. Let's look
at each.
- Download
    * client: read in path, ask main thread to read it
    * main: open the file, use `sendfile` to write it to the client's socket
- Upload
    * client: read in data, generate a file name, ask main thread to create the file
    * main: open the file for writing, write the contents

For the secure variants, the user must specify a private key (just a string of bytes
used as an xor key). They specify a length, which is mmapped, and the client
reads in the exact amount of bytes (i.e. in a read loop iterating until all
bytes have been read).

- Secure upload
    * same as before, except the client xors the data prior to asking the main thread to
        upload it
- Secure download
    * client: read in path, which cannot contain a `/`, handoff to main thread
    * main: executes this:
    ```c
    void handle_download_sec(struct ipc* ipc) {
        if (!ipc->encbuf)
            ipc->encbuf = malloc(MAX_FSZ);
        int fd = open(ipc->path, O_RDONLY);
        if (fd == -1) {
            ipc->buflen = 0;
            return;
        }
        long nread = read(fd, ipc->encbuf, MAX_FSZ);
        ipc->buflen = nread;
        close(fd);
    }
    ```
    * client: memcpy's `ipc->buflen` bytes from `ipc->encbuf` into a local stack buffer,
        xors with the privkey, and prints the resulting data

## Bugs

There are no path traversal checks for downloading a file,
so we can simply ask for `/proc/self/maps` to get some info leaks.

For secure download, the client checks that the path doesn't contain `/`, so path
traversal isn't possible. However, consider what happens if we ask for a directory
without a `/` character,
either `.` or `..`. The `open` call will succeed, however the subsequent `read` will
fail, setting `ipc->buflen` to `-1`. The client thread will then execute
`memcpy(buf, ipc->encbuf, ipc->buflen)`, resulting in an unbounded memcpy onto the thread
stack. However, the thread stack is surrounded by guard pages, so this memcpy
is guaranteed to segfault... This doesn't bring down the process due to the signal
handler `exit`ing the thread.

## Pwn

One might think a guaranteed segfault resulting in thread termination, where no other
userspace code touches the thread stack post-corruption (except to `munmap` it), would
be unexploitable. One would be wrong. The keyword here is userspace :)

The kernel provides a "robust list" api, to handle cases
where a thread terminates unexpectedly while still holding a futex
(which would normally cause deadlock, as the dead thread can't release the futex).
Userspace tells the kernel where the linked list head is with a syscall.
Then on thread exit, the kernel walks this list, and if it encounters
any futexes held by the exiting thread, it marks them with a special `FUTEX_OWNER_DIED`
value. For more info, the man page is
[here](https://man7.org/linux/man-pages/man2/set_robust_list.2.html)
and some other docs
[here](https://www.kernel.org/doc/Documentation/robust-futexes.txt).
There's also the
[source itself](https://elixir.bootlin.com/linux/v5.9.1/source/kernel/futex.c#L3545)
which isn't too bad to read, and indicates the futexes on the list must be
4-byte aligned.

Normally this api is handled internally by glibc, and the robust list head,
being a thread-specific concept, is naturally stored in tls (thread-local-storage).
For pthreads, tls is placed 'inline' directly after the stack, meaning we can corrupt
it with our unbounded megasmash.

A futex is really just a 4-byte int, and the value is the thread id of
the current owner. So in other words, on thread exit, the kernel walks a linked
list containing aligned 4-byte ints, and replaces any of them that are the
current thread id with `FUTEX_OWNER_DIED` (`0x40000000`).

Remember that we are in a fresh pid namespace, so thread id's will be allocated
starting at 2. Meaning, by hijacking the robust list,
we obtain the primitive of overwriting any small-ish 4-byte aligned
number with `0x40000000`.

It'd be tempting to target a length, say ask for a read of size 2, then overwrite
the length on the stack, however I don't think this is possible with how
the binary is compiled. Instead, we will target the unsigned char state variable
in the ipc struct, whose idle value is 2.
Since the state is an unsigned char, the `0x40000000` will be interpreted as
`0`, which means the slot is free in the array.

This gives us the following overall plan of attack:
- create a helper thread, which will have an idle state of 2,
    mmap a privkey of size `0x6000`, but leave it hanging
    in a read syscall partway through reading the privkey
- trigger the bug in a thread with id 2, corrupt the robust list such that
    it will change the helper thread's state to free
- reclaim the helper's slot in the array with a new connection, and immediately close it.
    this triggers the thread cleanup code, which will munmap the privkey
    (the helper thread however, is still hanging in the read syscall, asking to read
    into this munmapped data)
- create a victim thread, whose stack (of size `0x6000`) will get allocated at the
    same address we just munmapped
- send data to the helper thread, which will now be reading onto the victim thread's
    stack, giving us rop in the seccomped thread
- read a new ropchain onto the main thread's stack, dup2 and execve
