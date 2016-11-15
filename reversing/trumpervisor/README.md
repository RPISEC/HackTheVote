Reversing 400 (Raise to 500 if no solves within 12 hours)

Trumpervisor

Flag: flag{HyP3rv1s04z_aRe_T3h_fuTuR3}

State: NM
Influence: 5
Reaction: 10



We found a flash drive on the floor today. The flash drive had this binary on it and a text file that said 'Make Virtualization Great Again!' Naturally, we need someone to look into this. These files are way too suspicious to overlook, especially this close to the election. Can you tell us what this binary is doing?

`nc trumpervisor.pwn.republican 9000`

[Trumpervisor](https://s3.amazonaws.com/hackthevote/Trumpervisor.bf38753e7bfc93d1bbf9aee6aa6dbdcd39d2ccd31f1547253a75209419f0828a.sys)

EDIT: The bytes at 0x140002240 should be d6ff72e7cbbd3dae9ebd3dae9ebd3dae9ebd3dae9ebd3dae9ebd3dae9ebd3dfd (hex decoded of course)
