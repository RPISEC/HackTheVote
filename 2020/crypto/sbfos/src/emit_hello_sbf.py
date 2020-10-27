import struct

__NR_write = 1
__NR_writev = 20
__NR_execve = 59

msg = 'Hello, world!'

class BFEmitter:
    def __init__(self, program='', cell=0):
        self.program = program
        self.cell = cell
    def __repr__(self):
        return 'BFEmitter(program=%r, cell=%r)' % (self.program, self.cell)
    def move_to_cell(self, n):
        delta = n - self.cell
        if delta > 0:
            self.program += '>' * delta
        elif delta < 0:
            self.program += '<' * -delta
        self.cell = n
    def add_const(self, i, n):
        self.move_to_cell(i)
        if n > 0:
            self.program += '+' * n
        elif n < 0:
            self.program += '-' * (-n)
    def dup(self, i, j, k):
        self.move_to_cell(i)
        self.program += '['
        self.move_to_cell(j)
        self.program += '+'
        self.move_to_cell(k)
        self.program += '+'
        self.move_to_cell(i)
        self.program += '-]'
    def add(self, i, j):
        self.move_to_cell(i)
        self.program += '['
        self.move_to_cell(j)
        self.program += '+'
        self.move_to_cell(i)
        self.program += '-]'
    def mul_const(self, i, j):
        self.move_to_cell(i)
        self.program += '[>' + '+'*j + '<-]'
    def two_to_cell(self, i, j):
        self.add_const(j, 1)
        self.move_to_cell(i)
        self.program += '[-'
        self.mul_const(j, 2)
        self.add(j+1, j)
        self.move_to_cell(i)
        self.program += ']'
    def emit_24bit(self, i, n):
        for j in range(24):
            if n & (1 << j):
                #self.program += '/* %d %d %d */' % (n, j, 1 << j)
                if j > 5:
                    self.add_const(i+1, j)
                    self.two_to_cell(i+1, i+2)
                    self.add(i+2, i)
                else:
                    self.add_const(i, 2**j)
    def load_addr(self, i, j):
        self.move_to_cell(i)
        self.program += ','
        self.add_const(i, (j-i)*8)
x = BFEmitter()
x.add_const(0, 5)
x.add_const(5, 3)
x.add_const(3, 1)
x.dup(0, 1, 2)
x.add(2, 1)

print(x)

y = BFEmitter()
y.add_const(0, 5)
y.mul_const(0, 5)
y.two_to_cell(1, 4)

print(y)

z = BFEmitter()
z.add_const(0, 22)
z.two_to_cell(0, 1)

print(z)

w = BFEmitter()
w.emit_24bit(0, struct.unpack('<I', 'Hel\0')[0])
w.emit_24bit(1, struct.unpack('<I', 'lo!\0')[0])
w.load_addr(2, 0)
w.add_const(3, 3)
w.load_addr(4, 1)
w.add_const(5, 3)
w.add_const(6, __NR_writev)
w.add_const(7, 1)
w.load_addr(8, 2)
w.add_const(9, 2)
w.move_to_cell(6)
w.program += '.'

print(w)

with open('foo.sbf', 'w') as f:
    f.write(w.program+'\n')

def string_emitter(s):
    e = BFEmitter()
    n = len(s)/3
    for i in range(n):
        # slices of the string
        t = s[3*i:3*(i+1)]+'\0'
        print('%r %r' % (i, t))
        e.program += '/* %d %d */' % (i, struct.unpack('<I', t)[0])
        e.emit_24bit(i, struct.unpack('<I', t)[0])
    for i in range(n):
        # iovecs pointing to the slices
        print('%r %r' % (2*i+n, 2*i+n+1))
        e.load_addr(2*i+n, i)
        e.add_const(2*i+n+1, 3)
    print('%r' % (3*n,))
    e.add_const(3*n, __NR_writev)
    e.add_const(3*n+1, 1) # stdout
    e.load_addr(3*n+2, n) # iovec
    e.add_const(3*n+3, n) # number of iovecs
    e.move_to_cell(3*n)
    e.program += '.' # syscall
    return e

a = string_emitter('Hello, world!\n\0')

print(a)

with open('hello_world.sbf', 'w') as f:
    f.write(a.program+'\n')
