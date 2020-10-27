#include "tetris.h"

void init_game(game_state * game)
{
    memset(game, 0, sizeof(game_state));
    
    int i;
    for (i = 0; i < 7; i++) game->bag[i] = i;
    game->bag_index = -1;
    get_next_mino(game);

    game->lose = game_over;
    game->board.hold.dim = 1337;
}

void init_active_mino(game_state * game, uint64_t mino, int dim)
{
    game->board.active.repr = mino;
    game->board.active.dim = dim;
    game->board.active.x = 3;
    game->board.active.y = HEIGHT;
}

void get_next_mino(game_state * game)
{
    if (game->bag_index < 0 || game->bag_index >= 7)
    {
        shuffle(game->bag, 7);
        game->bag_index = 0;
    }

    switch (game->bag[game->bag_index++])
    {
        case 0:
            init_active_mino(game, L, dimL);
            break;
        case 1:
            init_active_mino(game, J, dimL);
            break;
        case 2:
            init_active_mino(game, S, dimL);
            break;
        case 3:
            init_active_mino(game, Z, dimL);
            break;
        case 4:
            init_active_mino(game, T, dimT);
            break;
        case 5:
            init_active_mino(game, I, dimI);
            break;
        case 6:
            init_active_mino(game, O, dimO);
            break;
        default:
            break;
    }
}

int check_collision(board_state * board, mino_state * mino)
{
    int val;
    int x, y;
    int a, b;
    for (x = 0; x < mino->dim; x++)
    {
        a = x + mino->x;
        for (y = 0; y < mino->dim; y++)
        {
            b = y + mino->y;

            val = get_mino_val(mino->repr, mino->dim, x, y);
            if (val)
            {
                if (a < 0 || a > 9)
                {
                    return 1;
                }
                else if (b < 0)
                {
                    return 2;
                }
                else if (get_board_val(board, a, b))
                {
                    return 4;
                }
            }
        }
    }
    return 0;
}

void soft_drop(board_state * board)
{
    do
    {
        board->active.y--;
    }
    while (!check_collision(board, &board->active));
    board->active.y++;
}

void hard_drop(board_state * board)
{
    soft_drop(board);
    lock_mino(board);
}

void move_left(board_state * board)
{
    board->active.x--;
    if (check_collision(board, &board->active)) board->active.x++;

}

void move_right(board_state * board)
{
    board->active.x++;
    if (check_collision(board, &board->active)) board->active.x--;
}

void rotate_softdrop(mino_state * mino)
{
    int ry = -1;
    uint64_t res = 0;

    int val;
    int x, y;
    for (y = 0; y < mino->dim; y++)
    {
        for (x = 0; x < WIDTH; x++)
        {
            val = get_mino_val(mino->repr, mino->dim, x, y);
            if (val)
            {
                if (ry < 0) ry = 0;
                res = set_mino_val(res, mino->dim, x, ry, val);
            }
        }
        if (ry != -1) ry++;
    }

    mino->repr = res;
}

void try_rotate(board_state * board, mino_state * mino)
{
    if (check_collision(board, mino))
    {
        mino->y -= 1;
        if (check_collision(board, mino))
        {
            mino->y += 2;
            if (check_collision(board, mino))
            {
                mino->y -= 1;
                mino->x += 1;
                if (check_collision(board, mino))
                {
                    mino->x -= 2;
                    if (check_collision(board, mino))
                    {
                        return;
                    }
                }
            }
        }
    }

    board->active.x = mino->x;
    board->active.y = mino->y;
    board->active.repr = mino->repr;
}

void padding(game_state * g, board_state * b, mino_state * m)
{
    int a;
    int asdf[90];
    int c;
    for (a = 0; a < 16; a++)
    {
        a = c;
    }
}


void active_rotate_left(board_state * board)
{
    mino_state test;
    test.x = board->active.x;
    test.y = board->active.y;
    test.dim = board->active.dim;
    test.repr = rotate_left(board->active.repr, test.dim);

    //rotate_softdrop(&test);
    try_rotate(board, &test);
}

void active_rotate_right(board_state * board)
{
    mino_state test;
    test.x = board->active.x;
    test.y = board->active.y;
    test.dim = board->active.dim;
    test.repr = rotate_right(board->active.repr, test.dim);

    //rotate_softdrop(&test);
    try_rotate(board, &test);
}

char get_input()
{
    char res = getchar();
    while (getchar() != '\n');
    return res;
}

void handle_event(game_state * game, char input)
{
    switch (input)
    {
        case 'l':
            move_left(&game->board);
            break;
        case '\'':
            move_right(&game->board);
            break;
        case 'p':
            hard_drop(&game->board);
            clear_rows(&game->board);
            get_next_mino(game);
            break;
        case ';':
            soft_drop(&game->board);
            break;
        case 'x':
            active_rotate_left(&game->board);
            break;
        case 'c':
            active_rotate_right(&game->board);
            break;
        case 'z':
            hold_mino(game);
            break;
        default:
            break;
    }
}

void game_over(board_state * board)
{
    system("clear");
    draw_board(board);
    puts("You're fired!");
    exit(1);
}

int blah(int asdf)
{
    __asm__("pop %ebx;"
            "pop %ebp;"
            "leave;"
            "ret;"
            "push %ebp;"
            "mov %esp, %ebp;");
    return;
}

void hold_mino(game_state * game)
{
    mino_state tmp;
    tmp.dim = game->board.active.dim;
    tmp.repr = game->board.active.repr;

    if (game->board.hold.dim == 1337)
    {
        get_next_mino(game);
    }
    else
    {
        game->board.active.x = 3;
        game->board.active.y = HEIGHT;
        game->board.active.dim = game->board.hold.dim;
        game->board.active.repr = game->board.hold.repr;
    }

    game->board.hold.dim = tmp.dim;
    game->board.hold.repr = tmp.repr;
}

int main()
{
    srand(get_input());

    game_state game;
    init_game(&game);

    while (1)
    {
        puts("\033c");
        puts("Tetrump Ultimate");
        puts("-------------------");
        if (game.board.hold.dim != 1337) draw_mino(game.board.hold.repr, game.board.hold.dim);
        puts("-------------------");
        draw_mino(game.board.active.repr, game.board.active.dim);
        puts("-------------------");
        draw_board(&game.board);
        handle_event(&game, get_input());
        if (check_collision(&game.board, &game.board.active)) game.lose((board_state*)&game.board.repr);
    }

    return 0;
}

