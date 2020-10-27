#include "minos.h"

int dimL = 3;
int dimJ = 3;
int dimZ = 3;
int dimS = 3;
int dimT = 3;
int dimI = 4;
int dimO = 4;

uint64_t L = 0x1248000;
uint64_t J = 0x2480400;
uint64_t Z = 0x924000;
uint64_t S = 0x3603600;
uint64_t T = 0x5b45000;
uint64_t I = 0xdb6000000000;
uint64_t O = 0x1f81f8000;

uint64_t set_bit(uint64_t num, int n, int val)
{
    uint64_t tmp = 1;
    return num ^ ((-val ^ num) & (tmp << n));
}

int get_mino_val(uint64_t mino, int dim, int x, int y)
{
    int n = ((dim-y-1)*3*dim) + (x*3);
    return (mino >> n) & 7;
}

uint64_t set_mino_val(uint64_t mino, int dim, int x, int y, int val)
{
    int n = ((dim-y-1)*3*dim) + (x*3);

    mino = set_bit(mino, n, val & 1);
    mino = set_bit(mino, n+1, val & 2);
    return set_bit(mino, n+2, val & 4);
}

uint64_t rotate_right(uint64_t mino, int dim)
{
    uint64_t res = 0;

    int x;
    int y;
    int val;
    for (y = 0; y < dim; y++)
    {
        for (x = 0; x < dim; x++)
        {
            val = get_mino_val(mino, dim, dim - y - 1, x);
            if (val)
            {
                res = set_mino_val(res, dim, x, y, val);
            }
        }
    }
    return res;
}

uint64_t rotate_left(uint64_t mino, int dim)
{
    uint64_t res = 0;

    int x;
    int y;
    int val;
    for (y = 0; y < dim; y++)
    {
        for (x = 0; x < dim; x++)
        {
            val = get_mino_val(mino, dim, y, dim - x - 1);
            if (val)
            {
                res = set_mino_val(res, dim, x, y, val);
            }
        }
    }
    return res;
}

void draw_mino(uint64_t mino, int dim)
{
    int x;
    int y;
    int val;
    for (y = dim - 1; y >= 0; y--)
    {
        for (x = 0; x < dim; x++)
        {
            val = get_mino_val(mino, dim, x, y);
            if (val)
            {
                printf("%d ", val);
            }
            else
            {
                printf("  ");
            }
        }
        puts("");
    }
}

