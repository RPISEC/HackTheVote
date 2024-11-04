# Setup
Use the pre-built `bzImage` and `rootfs` binaries provided

## Otherwise
* build the linux kernel (`x86_64`, defconfig, v5.4), `bzImage` will be in `arch/x86_64/boot`
* build `micropython/ports/linux-kernel` with the `main.c` replaced with the one here and `KDIR=<linux kernel build dir>`
* build busybox and create an initramfs containing the `mpy.ko` module from micropython
* `gcc -static mpy_interact.c -o mpy_interact`, copy to initramfs
* set up `init` to load the module and auto run the interact binary
