from collections import defaultdict
from pathlib import Path

from pwn import remote, context

HOST = "soviet-bloc-device.chal.hackthe.vote"
PORT = 1337

r = remote(HOST, PORT)

PIECES_BINARY = {
    'I': [0x0f00, 0x2222, 0x0f00, 0x2222],
    'O': [0x0660, 0x0660, 0x0660, 0x0660],
    'J': [0x00e2, 0x044c, 0x008e, 0x0644],
    'L': [0x00e8, 0x0c44, 0x002e, 0x0446],
    'S': [0x006c, 0x08c4, 0x006c, 0x08c4],
    'Z': [0x00c6, 0x0264, 0x00c6, 0x0264],
    'T': [0x00e4, 0x04c4, 0x004e, 0x0464],
}

# lol
PIECES = {name: [[[True if rotation & (1 << ((3 - row) * 4 + (3 - col))) else False for col in range(4)] for row in range(4)] for rotation in piece] for name, piece in PIECES_BINARY.items()}

START_ROWS = {
    'I': -1,
    'O': -1,
    'J': -2,
    'L': -2,
    'S': -2,
    'Z': -2,
    'T': -2,
}

def lfsr(seed):
    seed ^= (seed >> 7) & 0xffff;
    seed ^= (seed << 9) & 0xffff;
    seed ^= (seed >> 13) & 0xffff;
    return seed

class Tetris:
    def __init__(self):
        self.board = [[False] * 10 for _ in range(16)]
        self.seed = lfsr(0x1337)
        self.next_piece()

    def step(self, move):
        if self.move(move):
            self.place_piece()
            self.next_piece()

    def move(self, move):
        self.seed = lfsr(self.seed)

        match move:
            case 'a':
                col = self.col - 1
                if self.check_collision(self.piece, self.rotation, self.row, col):
                    self.col = col
            case 'd':
                col = self.col + 1
                if self.check_collision(self.piece, self.rotation, self.row, col):
                    self.col = col
            case 's':
                row = self.row + 1
                if self.check_collision(self.piece, self.rotation, row, self.col):
                    self.row = row
                else:
                    return True
            case 'j':
                rotation = (self.rotation + 3) % 4
                if self.check_collision(self.piece, rotation, self.row, self.col):
                    self.rotation = rotation
            case 'k':
                rotation = (self.rotation + 1) % 4
                if self.check_collision(self.piece, rotation, self.row, self.col):
                    self.rotation = rotation
            case '.':
                pass
        return False


    def check_collision(self, piece, rotation, row, col):
        for i in range(4):
            for j in range(4):
                abs_row = row + i
                abs_col = col + j
                if PIECES[piece][rotation][i][j] and \
                    (abs_row < 0 or abs_row >= 16 or
                     abs_col < 0 or abs_col >= 10 or self.board[abs_row][abs_col]):
                    return False
        return True

    def place_piece(self):
        for i in range(4):
            for j in range(4):
                if PIECES[self.piece][self.rotation][i][j]:
                    self.board[i + self.row][j + self.col] = True
        for i in reversed(range(16)):
            while all(self.board[i]):
                self.clear_row(i)

    def next_piece(self):
        self.piece = list(PIECES.keys())[self.seed % 7]
        self.rotation = 0
        self.row = START_ROWS[self.piece]
        self.col = 3

    def clear_row(self, row):
        for i in reversed(range(row + 1)):
            if i == 0:
                self.board[i] = [False] * 10
            else:
                self.board[i] = self.board[i - 1]

    def print(self):
        for i in range(16):
            for j in range(10):
                if ((i >= self.row and i < self.row + 4) and
                    (j >= self.col and j < self.col + 4) and
                     PIECES[self.piece][self.rotation][i - self.row][j - self.col]):
                    print('#', end='')
                    continue
                print('#' if self.board[i][j] else '.', end='')
            print()

    def read(self):
        result = 0
        for i in range(8):
            for j in range(8):
                result |= self.board[15 - i][9 - j] << (8 * i + j)
        return result

# Approach based off the tetris impl in http://tom7.org/papers/murphy2022harder.pdf
class Solver:
    def __init__(self):
        self.tetris = Tetris()
        self.seed = lfsr(0x1337)

        self.sols = defaultdict(list)
        with open(Path(__file__).parent / 'solutions.txt') as f:
            for line in f.read().splitlines():
                byte, sol = line.split()
                for i in range(0, len(sol), 3):
                    piece = sol[i]
                    rotation = int(sol[i + 1])
                    col = 'abcdefghijkl'.index(sol[i + 2]) - 2
                    self.sols[int(byte, 16)].append((piece, rotation, col))

    def execute(self, moves):
        for move in moves:
            self.tetris.step(move)

    def play(self, solution):
        out = ''
        for i in range(len(solution)):
            piece, rotation, col = solution[i]

            # Move piece down 1 row to give it room to rotate
            movelist = 's' + 'k'*rotation

            # Move piece over to its designated column
            if col < 3:
                movelist += 'a'*(3 - col)
            elif col > 3:
                movelist += 'd'*(col - 3)

            # Drop piece straight down
            row = START_ROWS[piece] + 1
            while self.tetris.check_collision(piece, rotation, row + 1, col):
                row += 1
                movelist += 's'

            # Stall lfsr by waiting until the next piece would be what we want
            for c in movelist:
                self.seed = lfsr(self.seed)
            if i < len(solution) - 1:
                while list(PIECES.keys())[lfsr(self.seed) % 7] != solution[i + 1][0]:
                    self.seed = lfsr(self.seed)
                    movelist += '.'

            # Lock piece in and get next piece
            movelist += 's'
            self.seed = lfsr(self.seed)

            out += movelist
            self.execute(movelist)
        return out

    def solve(self, nums):
        # Start with all-clear into S piece setup
        solution = [('J', 2, 0), ('O', 0, 7), ('I', 0, 4), ('I', 0, 4), ('J', 0, 1), ('S', 1, 0)]
        for num in nums:
            solution += self.sols[num]
        return self.play(solution)

for _ in range(5):
    s = Solver()
    r.recvuntil(b'challenge: ')
    challenge = bytes.fromhex(r.recvline().strip().decode())[::-1]
    r.sendline(s.solve(challenge).encode())
    print(r.recvline())
print(r.recvline())
