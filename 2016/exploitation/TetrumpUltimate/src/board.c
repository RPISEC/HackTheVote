#include "board.h"

int get_board_bit(board_state * board, int n)
{
    unsigned char tmp = *(board->repr + n/8);
    //unsigned char mask = (0x1 << (8 - n%8 - 1));
    unsigned char mask = (0x1 << (n%8));
    return (tmp & mask) > 0;
}

void set_board_bit(board_state * board, int n, int val)
{
    unsigned char * pTmp = board->repr + n/8;
    //unsigned char mask = (0x1 << (8 - n%8 - 1));
    unsigned char mask = (0x1 << ( n%8 ));

    if (val)
    {
        *pTmp |= mask;
    }
    else
    {
        *pTmp &= ~mask;
    }
}

int get_board_val(board_state * board, int x, int y)
{
    int n = ((y * 3 * WIDTH)+(x*3));
    int res = 0;
    
    res = get_board_bit(board, n);
    res |= get_board_bit(board, n+1) << 1;
    return res | (get_board_bit(board, n+2) << 2);
}

void set_board_val(board_state * board, int x, int y, int val)
{
    int n = ((y * 3 * WIDTH)+(x*3));
    set_board_bit(board, n, val & 1);
    set_board_bit(board, n+1, val & 2);
    set_board_bit(board, n+2, val & 4);
}

void lock_mino(board_state * board)
{
    int val;
    int x, y;
    for (x = 0; x < board->active.dim; x++)
    {
        for (y = 0; y < board->active.dim; y++)
        {
            val = get_mino_val(board->active.repr, board->active.dim, x, y);
            if (val)
            {
                set_board_val(board, board->active.x + x, board->active.y + y, val);
            }
        }
    }
}

void clear_rows(board_state * board)
{
    int skip;
    int x, y;
    for (y = 0; y < HEIGHT; y++)
    {
        skip = 0;
        for (x = 0; x < WIDTH; x++)
        {
            if (!get_board_val(board, x, y))
            {
                skip = 1;
                break;
            }
        }
        if (!skip)
        {
            int x;
            int ay;
            int val;
            for (ay = y; ay < HEIGHT; ay++)
            {
                for (x = 0; x < WIDTH; x++)
                {
                    val = get_board_val(board, x, ay+1);
                    set_board_val(board, x, ay, val);
                }
            }

            for (x = 0; x < WIDTH; x++) set_board_val(board, x, HEIGHT-1, 0);
            //memmove(board->repr + y*WIDTH*3, board->repr + (y+1)*WIDTH*3, sizeof(board->repr) - (y+1)*WIDTH*3);
            //memset(board->repr + (HEIGHT-1)*WIDTH*3, 0, WIDTH*3);
        }
    }
}

void draw_board(board_state * board)
{
    int x, y;
    int aval, bval;
    mino_state mino;
    for (y = (HEIGHT+0)- 1; y >= 0; y--)
    {
        for (x = 0; x < WIDTH; x++)
        {
            mino = board->active;

            aval = 0;
            bval = get_board_val(board, x, y);
            if (mino.y != 123 &&
                (mino.x <= x && x < (mino.x + mino.dim)) &&
                (mino.y <= y && y < (mino.y + mino.dim)))
            {
                aval = get_mino_val(mino.repr, mino.dim,
                                    x - mino.x, y - mino.y);
            }

            if (aval)
            {
                printf("%d ", aval);
            }
            else if (bval)
            {
                printf("%d ", bval);
            }
            else
            {
                printf("_ ");
            }
        }
        puts("");
    }
}

