Reversing 250

Machines (of The State)

Flag: flag{4nd_h15_N4m3_W4s_R1cH4rds}

State: UT



So we found this fancy new electronic CyberVoteLock (tm) on some voting machines. Lockpicks won't cut it for this one.
I got some poor EE student to extract the schematic, but I didn't take ecse4770. You're good with computers. Can you take a look?

`nc machines.pwn.republican 9000`

[machines_of_the_state](https://s3.amazonaws.com/hackthevote/machines_of_the_state.057399f8a2f1497357c9c585f1649296940a4cca721cc13370f5c29a34d834f6.tar.gz)

EDIT: 
	Input to the server should be in the form of a zero-padded hex-encoded byte string: to send the sequence [1] [3] [3] [7], send the server 01030307. 
    The keypad is attached where indicated in the schematic and behaves like a typical 4x4 keypad attached to a 74xx922.
