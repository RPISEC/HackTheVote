Trumpervisor
---

Trumpervisor is a Windows 10 x64 driver that loads a hypervisor underneath Windows 10.

The challenge has a couple of components:

	1. The driver has an IOCTL that xor's an encoded fake flag a value and then prints out the result.

		The goal of the challenge is to get this function to print out the fake flag.

		The value that is used for xoring depends on the math performed during 2.

	2. During hypervisor setup, the driver performs some math based on fixed values. These math operations modify the value used for xoring in 1.

		When the hypervisor is first installed by the driver, a number of data structures need to be built and the cpu needs to be configured.

		right before this setup starts, the driver saves the current registers. After setup is complete, a context switch is made and hese registers are used as the guests' register state.

		Throughout the setup code, some math is added in. This math uses the saved registers to perform math on a buffer in memory.

		There are a total of 6 chunks of math operations hidden in the hypervisor setup code.

	3. In the hypervisor setup code, the hypervisor configures a custom vmcall (think syscall, but for hypervisors).

		This vmcall is sort of legacy and not used to do anything real, but i left it in as a hint of sorts. 

		The driver can handle 2 ioctls. 1 ioctl does the xoring mentioned previously, the other ioctl simply calls vmcall.

		if you RE the vmcall, you will see it accessing this global value that is used for xoring the flag.

The challenge is to determine a guest register state that will lead to the flag getting decoded correctly.

I wrote a python script (see ../setup/) to ask for values of registers from a user and check them.

This script should be listening on a port via socat or something. 
