format ELF executable
segment readable writeable executable

SYS_EXIT_32BIT=1
SYS_EXIT_64BIT=60
SYS_WRITE=4
SYS_READ_64=0
STDIN=0
STDERR=2

macro fuckup64 {
    ; In x86_64 this is just a mov
    ; In i386 this becomes
    ; dec eax
    ; mov edi, 0x0
    ; lfence
    ; mov eax, <bytes from the next instruction>
    ; <problems>
    mov r15, 0xb8e8ae0f00000000
}

macro fuckup32 {
    ; x86_64 thinks the dec eax is a REX.W
    ; Turning the mov eax into mov rax/imm64
    ; But we only have a 32-bit int so the next 4
    ; bytes are eaten
    dec eax
    mov eax, 0
}

macro jmpto64 addr {
    ; Far jmp to segment 0x33 means enter 64-bit mode
    dec eax ; This doubles as fuckup64
    mov eax, 0x23
    push eax
    dec eax
    or al, 0x13
    push eax
    push addr
    retf

    ; This is a long version of:
    ; push 0x23
    ; jmp 0x33:addr
}

macro jmpto32 addr {
    push 0 ; Otherwise we run out of stack
    mov rax, 0x0000002300000000
    shr rax, 24
    ; push; retf is the x86_64 equivalent of far jmp
    ; segment 0x23 means enter 32 bit mode
    mov dword[rsp+0x4], 0
    mov byte [rsp+0x7], ah
    mov dword[rsp], addr
    retf

    ; This is a long version of
    ; push 0
    ; mov dword[rsp+0x4], 0x23
    ; mov dword[rsp], addr
    ; retf
}

main:
entry $
    dec eax
    mov ax, cs
    cmp ax, 0x23 ; 32 bit process on 64 bit kernel has this selector in CS
    jne problems32
    push eax ; push 0x23
    or al, 0x13 ; eax = 0x33
    push eax ; push 0x33
    push start64
    retf ; jmp far 0x33:start64 jmps to 64 bit mode
use64
start64:

    ; Get input
    ; These get xor'd to zero right after, but MAN do they do a number on Hopper
    mov rax, 0xdf3a0f66090f1b37
    mov rdi, 0xe9f4e2ebe86423ca
    xor eax, eax
    xor rdi, rdi
    mov rsi, input
    mov rdx, msgLen
    syscall

    ; finishLabel = end32
    ; for (int i = 0; i < msgLen - 1; i ++) {
    ;     if (input[i] ^ 0x42 != msg[i]) finishLabel = problems32
    ; }
    ; goto finishLabel

    mov rdx, now32
    mov ecx, 0
xorloop64:
    ; Loading 64-bit immediate values is a disaster in 32-bit disassembly
    ; The top 4 bytes of this are fake x86 instructions
    ; The bottom 4 bytes are random
    mov rbx, 0x358d0150819cf3c4
    ror rbx, cl
    
    cmp ecx, msgLen
    je done

    mov al, [input + ecx]
    xor al, bl
 
    fuckup64
    
    cmp al, [msg + ecx]
    je goodletter
    jmpto32 badletter32

use32
badletter32:
    fuckup32 
    mov edx, problems32
    inc ecx
    jmpto64 xorloop64

use64
goodletter:
    jmpto32 goodletter32

use32
goodletter32:
    fuckup32
    xchg edx, edx
    inc ecx
    jmpto64 xorloop64

use64
done:
    jmpto32 edx

use32
now32:
    jmpto64 end64
use64
end64:
    ; "Correct!"
    mov edx, yepLen
    mov ecx, yep
    mov ebx, STDERR
    mov eax, SYS_WRITE
    int 0x80
    mov eax, SYS_EXIT_64BIT
    syscall
    ud2

use32
problems32:
    ; "Nope!"
    mov edx, nopeLen
    mov ecx, nope
    mov ebx, STDERR
    mov eax, SYS_WRITE
    int 0x80
    dec ebx
    mov eax, SYS_EXIT_32BIT
    int 0x80

; Strings and shit
msg:
    db 162,142,144,31,71,240,252,159,135,38,72,175,162,212,44,78,175,145,13,70,116,124,89,119,177,31,82,35,60,232,29,204,96,204,103,87
msgLen = $-msg
yep:
    db "Correct!",10
yepLen = $-yep
nope:
    db "Nope!",10
nopeLen = $-nope
input:
    db 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
