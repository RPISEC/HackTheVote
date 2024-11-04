#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>

#define BOARD_WIDTH 10
#define BOARD_HEIGHT 16

const uint16_t PIECES[7][4] = {
    // I piece
    // .... ..#.
    // #### ..#.
    // .... ..#.
    // .... ..#.
    {0b0000111100000000, 0b0010001000100010, 0b0000111100000000, 0b0010001000100010},

    // O piece
    // ....
    // .##.
    // .##.
    // ....
    {0b0000011001100000, 0b0000011001100000, 0b0000011001100000, 0b0000011001100000},

    // J piece
    // .... .... .... ....
    // .... .#.. .... .##.
    // ###. .#.. #... .#..
    // ..#. ##.. ###. .#..
    {0b0000000011100010, 0b0000010001001100, 0b0000000010001110, 0b0000011001000100},

    // L piece
    // .... .... .... ....
    // .... ##.. .... .#..
    // ###. .#.. ..#. .#..
    // #... .#.. ###. .##.
    {0b0000000011101000, 0b0000110001000100, 0b0000000000101110, 0b0000010001000110},

    // S piece
    // .... .... .... ....
    // .... #... .... #...
    // .##. ##.. .##. ##..
    // ##.. .#.. ##.. .#..
    {0b0000000001101100, 0b0000100011000100, 0b0000000001101100, 0b0000100011000100},

    // Z piece
    // .... .... .... ....
    // .... ..#. .... ..#.
    // ##.. .##. ##.. .##.
    // .##. .#.. .##. .#..
    {0b0000000011000110, 0b0000001001100100, 0b0000000011000110, 0b0000001001100100},

    // T piece
    // .... .... .... ....
    // .... .#.. .... .#..
    // ###. ##.. .#.. .##.
    // .#.. .#.. ###. .#..
    {0b0000000011100100, 0b0000010011000100, 0b0000000001001110, 0b0000010001100100},
};

const int8_t START_ROWS[7] = {-1, -1, -2, -2, -2, -2, -2};

uint16_t __attribute__((noinline)) lfsr() {
    static uint16_t lfsr = 0x1337;
    lfsr ^= lfsr >> 7;
    lfsr ^= lfsr << 9;
    lfsr ^= lfsr >> 13;
    return lfsr;
}

bool __attribute__((noinline)) get_piece_block(int piece_num, int rotation, int row,
                                               int col) {
    int piece = PIECES[piece_num][rotation];
    int mask = 1 << ((3 - row) * 4 + (3 - col));
    return piece & mask;
}

enum Move {
    None,
    Left,
    Right,
    Down,
    RotateAntiClockwise,
    RotateClockwise,
};

enum Move get_move(char c) {
    switch (c) {
    case 'a':
        return Left;
    case 's':
        return Down;
    case 'd':
        return Right;
    case 'j':
        return RotateAntiClockwise;
    case 'k':
        return RotateClockwise;
    case '.':
        return None;
    default:
        fprintf(stderr, "invalid input\n");
        exit(1);
    }
}

struct Field {
    bool board[BOARD_HEIGHT][BOARD_WIDTH];
    uint8_t piece;
    uint8_t rotation;
    int8_t row;
    int8_t col;
    uint16_t lfsr_result;
};

struct Field *init_board() {
    uint16_t lfsr_result = lfsr();
    uint8_t piece = lfsr_result % 7;
    struct Field *field = calloc(1, sizeof(struct Field));
    field->piece = piece;
    field->row = START_ROWS[piece];
    field->col = 3;
    field->lfsr_result = lfsr_result;
    return field;
}

bool __attribute__((noinline)) check_collision(struct Field *field, int rotation, int row,
                                               int col) {
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            int abs_row = row + i;
            int abs_col = col + j;
            if (get_piece_block(field->piece, rotation, i, j) &&
                (abs_row < 0 || abs_row >= BOARD_HEIGHT || abs_col < 0 ||
                 abs_col >= BOARD_WIDTH || field->board[abs_row][abs_col])) {
                return false;
            }
        }
    }
    return true;
}

bool simulate_move(struct Field *field, enum Move m) {
    field->lfsr_result = lfsr();

    switch (m) {
    case Left: {
        int col = field->col - 1;
        if (check_collision(field, field->rotation, field->row, col))
            field->col = col;
        break;
    }
    case Right: {
        int col = field->col + 1;
        if (check_collision(field, field->rotation, field->row, col))
            field->col = col;
        break;
    }
    case Down: {
        int row = field->row + 1;
        if (check_collision(field, field->rotation, row, field->col)) {
            field->row = row;
            break;
        } else {
            return true;
        }
    }
    case RotateAntiClockwise: {
        int rotation = (field->rotation + 3) % 4;
        if (check_collision(field, rotation, field->row, field->col))
            field->rotation = rotation;
        break;
    }
    case RotateClockwise: {
        int rotation = (field->rotation + 1) % 4;
        if (check_collision(field, rotation, field->row, field->col))
            field->rotation = rotation;
        break;
    }
    default:
        break;
    }

    return false;
}

bool next_piece(struct Field *field) {
    uint8_t piece = field->lfsr_result % 7;
    field->piece = piece;
    field->rotation = 0;
    field->row = START_ROWS[piece];
    field->col = 3;

    return check_collision(field, field->rotation, field->row, field->col);
}

bool is_row_full(struct Field *field, int row) {
    for (int col = 0; col < BOARD_WIDTH; col++) {
        if (!field->board[row][col]) {
            return false;
        }
    }
    return true;
}

void clear_row(struct Field *field, int row) {
    for (int i = row; i >= 0; i--) {
        if (i == 0) {
            memset(field->board[i], 0, BOARD_WIDTH);
        } else {
            memcpy(field->board[i], field->board[i - 1], BOARD_WIDTH);
        }
    }
}

void place_piece(struct Field *field) {
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            if (get_piece_block(field->piece, field->rotation, i, j)) {
                field->board[i + field->row][j + field->col] = true;
            }
        }
    }

    for (int i = BOARD_HEIGHT - 1; i >= 0; i--) {
        while (is_row_full(field, i)) {
            clear_row(field, i);
        }
    }
}

bool run_step(struct Field *field, enum Move move) {
    if (simulate_move(field, move)) {
        place_piece(field);
        if (!next_piece(field)) {
            return false;
        }
    }
    return true;
}

void run(struct Field *field, char *input) {
    for (char move = *input; move != '\0'; move = *++input) {
        if (!run_step(field, get_move(move))) {
            break;
        }
    }
}

uint64_t __attribute__((noinline)) finish(struct Field *field) {
    uint64_t result = 0;
    for (int i = 0; i < 8; i++) {
        for (int j = 0; j < 8; j++) {
            result |= ((uint64_t)field->board[BOARD_HEIGHT - 1 - i][BOARD_WIDTH - 1 - j]
                       << (8 * i + j));
        }
    }
    return result;
}

int main(int argc, char *argv[]) {
    struct Field *field = init_board();

    if (argc != 2) {
        fprintf(stderr, "invalid input\n");
        exit(1);
    }
    run(field, argv[1]);

    uint64_t result = finish(field);
    printf("%016lx\n", result);

    free(field);
    return 0;
}
