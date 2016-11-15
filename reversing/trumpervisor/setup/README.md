check_solution.py needs to be running on a port via socat. 

It asks for a register state then evals the register state to see if the flag would have been decoded correctly by the hypervisor.

If so, it prints the correct flag. 