#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <string.h>
#include <ctype.h>
#include <time.h>
#include <inttypes.h>

#define LETTERS 5
#define SOLUTION_COUNT 32
#define GUESS_COUNT 37
#define PRINT_COLS 4
#define PRINT_ROWS 8

#define BLACK 0
#define GREEN 1
#define YELLOW 2

#define MAYBE 0
#define DEFINITELY 1
#define DEFINITELY_NOT 2

#ifndef DEBUG
#define DEBUG 0
#endif /* ndef DEBUG */

// From https://github.com/thesilican/duotrigordle/blob/main/src/store/wordlist.ts
#include "wordlist.h"

void init(void)
{
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}

int nextchar(void)
{
    do
    {
        int ch = getchar();
        if (!isspace(ch))
        {
            return ch;
        }
    } while(1);
}

struct word_t
{
    char letters[LETTERS];
};

struct game_t
{
    uint32_t seed;
    struct word_t guesses[GUESS_COUNT];
    struct word_t solutions[SOLUTION_COUNT];
    uint8_t auto_solves[SOLUTION_COUNT];
    uint8_t guess_count;
};

uint8_t check_word(const char* guess, const char* solution)
{
    return
        guess[0] == solution[0] &&
        guess[1] == solution[1] &&
        guess[2] == solution[2] &&
        guess[3] == solution[3] &&
        guess[4] == solution[4];
}

void score_word(struct word_t* guess, struct word_t* solution, uint8_t (*score)[LETTERS])
{
    for (uint8_t i = 0; i < LETTERS; i ++)
    {
        (*score)[i] = BLACK;

        if (guess->letters[i] == solution->letters[i])
        {
            // Correct letter correct position
            (*score)[i] = GREEN;
        }
        else
        {
            // Look for the answer having N of this letter
            // where N is >= the count of this letter in the guess so far
            // and ignore correct guesses
            uint8_t this_count = 0;
            for (uint8_t j = 0; j < i; j ++)
            {
                if (guess->letters[j] == solution->letters[j])
                {
                    continue;
                }
                if (guess->letters[j] == guess->letters[i])
                {
                    this_count ++;
                }
            }

            uint8_t correct_count = 0;
            for (uint8_t j = 0; j < LETTERS; j ++)
            {
                if (guess->letters[j] == solution->letters[j])
                {
                    continue;
                }
                if (solution->letters[j] == guess->letters[i])
                {
                    correct_count ++;
                }
            }

            if (correct_count > this_count)
            {
                (*score)[i] = YELLOW;
            }
        }
    }
}

void print_guess(struct word_t* guess, struct word_t* solution, int is_auto_solve)
{
    uint8_t scores[LETTERS];
    score_word(guess, solution, &scores);

    for (uint8_t i = 0; i < LETTERS; i ++)
    {
        const char* color = "\033[0m"; // clear
        switch (scores[i])
        {
        case BLACK:
        default:
            break;
        case GREEN:
            if (is_auto_solve)
            {
                color = "\033[1;30;45m"; // magenta
            }
            else
            {
                color = "\033[1;30;42m"; // green
            }
            break;
        case YELLOW:
            color = "\033[1;30;43m"; // yellow
            break;
        }

        printf("%s %c ", color, guess->letters[i]);
    }
    printf("\033[0m"); // clear
}

void print_game(struct game_t* game)
{
    // 8 rows of 4 boards

    // guess1   guess1   guess1   guess1
    // guess2   guess2   guess2   guess2
    // ...
    //
    // guess1   guess1   guess1   guess1
    // guess2   guess2   guess2   guess2
    // ...

    // Remember correct boards and don't draw them further
    char correct[SOLUTION_COUNT] = {0};

    // Remember "known" correct state
    struct word_t known_letters[SOLUTION_COUNT];

    for (uint8_t solution = 0; solution < SOLUTION_COUNT; solution ++)
    {
        known_letters[solution].letters[0] = ' ';
        known_letters[solution].letters[1] = ' ';
        known_letters[solution].letters[2] = ' ';
        known_letters[solution].letters[3] = ' ';
        known_letters[solution].letters[4] = ' ';
    }

    for (uint8_t row = 0; row < PRINT_ROWS; row ++)
    {
        for (uint8_t guess = 0; guess < game->guess_count; guess ++)
        {
            for (uint8_t col = 0; col < PRINT_COLS; col ++)
            {
                uint8_t solution = col + row * PRINT_COLS;
                uint8_t is_correct = check_word(&game->guesses[guess].letters[0], &game->solutions[solution].letters[0]);

                if (correct[solution])
                {
                    printf("               ");
                }
                else
                {
                    print_guess(&game->guesses[guess], &game->solutions[solution], is_correct && game->auto_solves[solution]);
                }
                if (col + 1 != PRINT_COLS)
                {
                    printf("      ");
                }

                if (is_correct)
                {
                    correct[solution] = 1;
                }

                if (game->guesses[guess].letters[0] == game->solutions[solution].letters[0])
                {
                    known_letters[solution].letters[0] = game->guesses[guess].letters[0];
                }
                if (game->guesses[guess].letters[1] == game->solutions[solution].letters[1])
                {
                    known_letters[solution].letters[1] = game->guesses[guess].letters[1];
                }
                if (game->guesses[guess].letters[2] == game->solutions[solution].letters[2])
                {
                    known_letters[solution].letters[2] = game->guesses[guess].letters[2];
                }
                if (game->guesses[guess].letters[3] == game->solutions[solution].letters[3])
                {
                    known_letters[solution].letters[3] = game->guesses[guess].letters[3];
                }
                if (game->guesses[guess].letters[4] == game->solutions[solution].letters[4])
                {
                    known_letters[solution].letters[4] = game->guesses[guess].letters[4];
                }
            }
            printf("\n");
        }

        for (uint8_t col = 0; col < PRINT_COLS; col ++)
        {
            uint8_t solution = col + row * PRINT_COLS;

            if (correct[solution])
            {
                printf("               ");
            }
            else
            {
                printf("---------------");
            }
            if (col + 1 != PRINT_COLS)
            {
                printf("      ");
            }
        }
        printf("\n");

        for (uint8_t col = 0; col < PRINT_COLS; col ++)
        {
            uint8_t solution = col + row * PRINT_COLS;

            if (correct[solution])
            {
                printf("               ");
            }
            else
            {
                print_guess(&known_letters[solution], &game->solutions[solution], 0);
            }
            if (col + 1 != PRINT_COLS)
            {
                printf("      ");
            }
        }
        printf("\n");
        printf("\n");
    }
}

void mark_auto_solve(struct game_t* game, struct word_t* word, uint8_t solution)
{
    game->auto_solves[solution] = 1;
    game->guesses[game->guess_count].letters[0] = word->letters[0];
    game->guesses[game->guess_count].letters[1] = word->letters[1];
    game->guesses[game->guess_count].letters[2] = word->letters[2];
    game->guesses[game->guess_count].letters[3] = word->letters[3];
    game->guesses[game->guess_count].letters[4] = word->letters[4];
    game->guess_count = game->guess_count + 1;
}

// I'd like to see ChatGPT try to recreate this
uint8_t run_auto_solver(struct game_t* game)
{
    // All letters known -> solved
    for (uint8_t solution = 0; solution < SOLUTION_COUNT; solution ++)
    {
        struct word_t known_letters;
        uint8_t is_correct = 0;
        for (uint8_t guess = 0; guess < game->guess_count; guess ++)
        {
            if (check_word(&game->guesses[guess].letters[0], &game->solutions[solution].letters[0]))
            {
                is_correct = 1;
                break;
            }

            if (game->guesses[guess].letters[0] == game->solutions[solution].letters[0])
            {
                known_letters.letters[0] = game->guesses[guess].letters[0];
            }
            if (game->guesses[guess].letters[1] == game->solutions[solution].letters[1])
            {
                known_letters.letters[1] = game->guesses[guess].letters[1];
            }
            if (game->guesses[guess].letters[2] == game->solutions[solution].letters[2])
            {
                known_letters.letters[2] = game->guesses[guess].letters[2];
            }
            if (game->guesses[guess].letters[3] == game->solutions[solution].letters[3])
            {
                known_letters.letters[3] = game->guesses[guess].letters[3];
            }
            if (game->guesses[guess].letters[4] == game->solutions[solution].letters[4])
            {
                known_letters.letters[4] = game->guesses[guess].letters[4];
            }
        }
        if (is_correct)
        {
            continue;
        }

        if (check_word(&known_letters.letters[0], &game->solutions[solution].letters[0]))
        {
            mark_auto_solve(game, &known_letters, solution);
            return 1;
        }
    }

    // 5 letters known and each letter only has 1 valid position
    for (uint8_t solution = 0; solution < SOLUTION_COUNT; solution ++)
    {
        // Ignore words we've already solved
        uint8_t is_correct = 0;
        for (uint8_t guess = 0; guess < game->guess_count; guess ++)
        {
            if (check_word(&game->guesses[guess].letters[0], &game->solutions[solution].letters[0]))
            {
                is_correct = 1;
                break;
            }
        }
        if (is_correct)
        {
            continue;
        }

        // Find all distinct letters used
        char letters_found[LETTERS];
        uint8_t found_count = 0;
        uint8_t green_found[LETTERS] = {0};

        for (uint8_t guess = 0; guess < game->guess_count; guess ++)
        {
            uint8_t score[LETTERS];
            score_word(&game->guesses[guess], &game->solutions[solution], &score);

            for (uint8_t letter = 0; letter < LETTERS; letter ++)
            {
                char guess_letter = game->guesses[guess].letters[letter];
                if (score[letter] == GREEN)
                {
                    if (!green_found[letter])
                    {
                        green_found[letter] = 1;
                        letters_found[found_count] = guess_letter;
                        found_count += 1;
                    }
                }
            }
        }
        for (uint8_t guess = 0; guess < game->guess_count; guess ++)
        {
            uint8_t score[LETTERS];
            score_word(&game->guesses[guess], &game->solutions[solution], &score);

            for (uint8_t letter = 0; letter < LETTERS; letter ++)
            {
                char guess_letter = game->guesses[guess].letters[letter];
                if (score[letter] == YELLOW)
                {
                    // Number of times this letter is seen in the found list
                    uint8_t found_this_count = 0;
                    for (uint8_t i = 0; i < found_count; i ++)
                    {
                        if (letters_found[i] == guess_letter)
                        {
                            found_this_count += 1;
                        }
                    }

                    // Count all of the non-black scored versions of this letter
                    uint8_t guess_this_count = 0;
                    for (uint8_t i = 0; i < LETTERS; i ++)
                    {
                        if (game->guesses[guess].letters[i] == guess_letter
                            && (score[i] == GREEN || score[i] == YELLOW))
                        {
                            guess_this_count += 1;
                        }
                    }

                    // If we don't have enough of this letter in the found list, find it
                    if (found_this_count < guess_this_count)
                    {
                        letters_found[found_count] = guess_letter;
                        found_count ++;
                    }
                }
            }
        }

        // If we don't know all the letters we can't possibly solve it
        if (found_count != 5)
        {
#if DEBUG
            printf(
                "Cannot solve %d %c%c%c%c%c: only found %d letters\n",
                solution,
                game->solutions[solution].letters[0],
                game->solutions[solution].letters[1],
                game->solutions[solution].letters[2],
                game->solutions[solution].letters[3],
                game->solutions[solution].letters[4],
                found_count
            );
#endif /* DEBUG */
            continue;
        }

        // Find the possible places for each letter
        uint8_t placement[LETTERS] = {0};
        uint8_t placement_found[LETTERS] = {0};

        // Worklist: finding the placement of one letter will rule out a Maybe in
        // other letters, which may then become placeable. So repeat this process
        // until no more letters can be placed.
        // Termination: Since known letters are ignored, either no new letters are
        // found (terminates) or a new letter is found (remaining count decreases)
        uint8_t any_updated = 0;
        do
        {
            any_updated = 0;

            // Try to find a place for each letter
            for (uint8_t f = 0; f < LETTERS; f ++)
            {
                // Already found, ignore
                if (placement_found[f])
                {
                    continue;
                }
                char found_letter = letters_found[f];

                // Dupe letter support: get how many of this letter exist
                // and which index of this letter this one is
                uint8_t found_this_index = 0;
                for (uint8_t i = 0; i < f; i ++)
                {
                    if (letters_found[i] == found_letter)
                    {
                        found_this_index += 1;
                    }
                }
                uint8_t found_this_count = 0;
                for (uint8_t i = 0; i < LETTERS; i ++)
                {
                    if (letters_found[i] == found_letter)
                    {
                        found_this_count += 1;
                    }
                }

                // Find all possible places for this letter
                uint8_t color[LETTERS] = {MAYBE};
                for (uint8_t f1 = 0; f1 < LETTERS; f1 ++)
                {
                    // Different letter already found: wherever it is, we are not
                    if (letters_found[f] != letters_found[f1] && placement_found[f1])
                    {
                        color[placement[f1]] = DEFINITELY_NOT;
                    }
                }
                // For all guesses, rule out/in the answers we know
                for (uint8_t guess = 0; guess < game->guess_count; guess ++)
                {
                    uint8_t score[LETTERS];
                    score_word(&game->guesses[guess], &game->solutions[solution], &score);
                    for (uint8_t letter = 0; letter < LETTERS; letter ++)
                    {
                        char guess_letter = game->guesses[guess].letters[letter];
                        if (guess_letter == found_letter)
                        {
                            // This letter in this position is yellow/black: definitely not here
                            if (score[letter] == YELLOW || score[letter] == BLACK)
                            {
                                color[letter] = DEFINITELY_NOT;
                            }
                            // This letter in this position is green: definitely here
                            if (score[letter] == GREEN)
                            {
                                color[letter] = DEFINITELY;
                            }
                        }
                        else
                        {
                            // Another letter in this position is green: definitely not here
                            if (score[letter] == GREEN)
                            {
                                color[letter] = DEFINITELY_NOT;
                            }
                            // Another letter in another position is green: don't care
                        }
                    }
                }

                uint8_t yesses = 0;
                uint8_t maybes = 0;
                for (uint8_t letter = 0; letter < LETTERS; letter ++)
                {
                    if (color[letter] == DEFINITELY)
                    {
                        yesses += 1;
                    }
                    if (color[letter] == MAYBE)
                    {
                        maybes += 1;
                    }
                }

                if (yesses == found_this_count)
                {
                    // If we have enough "yes" spots, we know we're in one of them
                    placement_found[f] = 1;
                    any_updated = 1;

                    // Pick the Nth "yes" spot where N is which index of the letter we are
                    uint8_t yes_index = 0;
                    for (uint8_t letter = 0; letter < LETTERS; letter ++)
                    {
                        if (color[letter] == DEFINITELY)
                        {
                            if (yes_index == found_this_index)
                            {
                                placement[f] = letter;
                                break;
                            }
                            yes_index += 1;
                        }
                    }
                }
                else if ((maybes + yesses) == found_this_count)
                {
                    // If we have exactly as many "maybe" and "yes" spots as counts of this letter
                    // then they are the only possible places it can go, and therefore the answer
                    placement_found[f] = 1;
                    any_updated = 1;

                    // Pick the Nth "maybe" or "yes" spot where N is which index of the letter we are
                    uint8_t maybe_index = 0;
                    for (uint8_t letter = 0; letter < LETTERS; letter ++)
                    {
                        if (color[letter] == DEFINITELY || color[letter] == MAYBE)
                        {
                            if (maybe_index == found_this_index)
                            {
                                placement[f] = letter;
                                break;
                            }
                            maybe_index += 1;
                        }
                    }
                }

#if DEBUG
                printf(
                    "Find letter %d %c%c%c%c%c: %c at %c\n",
                    solution,
                    game->solutions[solution].letters[0],
                    game->solutions[solution].letters[1],
                    game->solutions[solution].letters[2],
                    game->solutions[solution].letters[3],
                    game->solutions[solution].letters[4],
                    found_letter,
                    (placement_found[f] ? '1' + placement[f] : '?')
                );
#endif /* DEBUG */
            }
        } while (any_updated);

        // If we have a place for all the letters, we've solved it!
        uint8_t all_found = 1;
        for (uint8_t f = 0; f < LETTERS; f ++)
        {
            if (!placement_found[f])
            {
                all_found = 0;
                break;
            }
        }
        if (all_found)
        {
            struct word_t known_letters;
            for (uint8_t f = 0; f < LETTERS; f ++)
            {
                known_letters.letters[placement[f]] = letters_found[f];
            }

            // Sanity
            if (check_word(&known_letters.letters[0], &known_letters.letters[0]))
            {
                mark_auto_solve(game, &known_letters, solution);
                return 1;
            }
        }
    }

    return 0;
}

/*
int main(int argc, char** argv, char** envp)
{
    struct game_t game;

    init();

    printf("The thirty-twodle challenge! Enter game seed:\n");
    scanf("%" SCNx32, &game.seed);
    if (game.seed == 0)
    {
        return 1;
    }
    srand(game.seed);

    // Game setup
    game.guess_count = 0;
    for (uint8_t i = 0; i < SOLUTION_COUNT; i ++)
    {
        for (uint8_t j = 0; j < LETTERS; j ++)
        {
            game.solutions[i].letters[j] = 0;
        }
        game.auto_solves[i] = 0;
    }
    for (uint8_t i = 0; i < GUESS_COUNT; i ++)
    {
        for (uint8_t j = 0; j < LETTERS; j ++)
        {
            game.guesses[i].letters[j] = 0;
        }
    }

    // Game init
    for (uint8_t i = 0; i < SOLUTION_COUNT; i ++)
    {
        uint32_t which_word = rand() % word_list_count;
        for (uint8_t j = 0; j < LETTERS; j ++)
        {
            game.solutions[i].letters[j] = word_list[which_word][j];
        }
    }

    // Game play
    uint8_t winner = 0;
    for (uint8_t current = 0; current < GUESS_COUNT; current ++)
    {
        // If we can auto-solve any, do the next one
        if (run_auto_solver(&game))
        {
            print_game(&game);
            continue;
        }

        printf("Guess %d/%d: ", current + 1, GUESS_COUNT);
        game.guesses[current].letters[0] = nextchar();
        game.guesses[current].letters[1] = nextchar();
        game.guesses[current].letters[2] = nextchar();
        game.guesses[current].letters[3] = nextchar();
        game.guesses[current].letters[4] = nextchar();

        uint8_t found = 0;
        for (uint32_t word = 0; word < valid_word_list_count; word ++)
        {
            if (check_word(&valid_word_list[word][0], &game.guesses[current].letters[0]))
            {
                found = 1;
                break;
            }
        }
        if (!found)
        {
            printf("That's not a valid word! Check the valid word list :)\n");
            break;
        }

        game.guess_count = current + 1;

        print_game(&game);

        // If they got it correct, they win! End the game
        uint8_t all_correct = 1;
        for (uint8_t solution = 0; solution < SOLUTION_COUNT; solution ++)
        {
            uint8_t is_correct = 0;
            for (uint8_t guess = 0; guess < game.guess_count; guess ++)
            {
                if (check_word(&game.guesses[guess].letters[0], &game.solutions[solution].letters[0]))
                {
                    is_correct = 1;
                    break;
                }
            }
            if (!is_correct)
            {
                all_correct = 0;
                break;
            }
        }
        if (all_correct)
        {
            winner = 1;
            break;
        }
    }

    // Print results in copyable emoji squares
    printf("Thirty-Twodle Challenge #%x\n", game.seed);
    if (winner)
    {
        printf("Guesses: %hhu/%hhu\n", game.guess_count, GUESS_COUNT);
    }
    else
    {
        printf("Guesses: X/%hhu\n", GUESS_COUNT);
    }

    for (uint8_t row = 0; row < PRINT_ROWS; row ++)
    {
        for (uint8_t col = 0; col < PRINT_COLS; col ++)
        {
            uint8_t solution = col + row * PRINT_COLS;
            uint8_t is_correct = 0;
            uint8_t correct_guess = 0;
            for (uint8_t guess = 0; guess < GUESS_COUNT; guess ++)
            {
                if (check_word(&game.guesses[guess].letters[0], &game.solutions[solution].letters[0]))
                {
                    is_correct = 1;
                    correct_guess = guess + 1;
                    break;
                }
            }

            if (!is_correct)
            {
                printf("\xf0\x9f\x9f\xa5\xf0\x9f\x9f\xa5");
            }
            else if (game.auto_solves[solution])
            {
                printf("\xf0\x9f\x9f\xaa\xf0\x9f\x9f\xaa");
            }
            else
            {
                printf("%hhu\xEF\xB8\x8F\xE2\x83\xA3", correct_guess / 10);
                printf("%hhu\xEF\xB8\x8F\xE2\x83\xA3", correct_guess % 10);
            }
            printf(" ");
        }
        printf("\n");
    }

    uint8_t auto_solve_count = 0;
    for (uint8_t solution = 0; solution < SOLUTION_COUNT; solution ++)
    {
        if (game.auto_solves[solution])
        {
            auto_solve_count ++;
        }
    }

    if (winner && auto_solve_count >= DIFFICULTY)
    {
        printf("You solved the challenge!\n");
        system("/bin/sh");
        return 0;
    }

    if (winner)
    {
        printf("You may have solved the puzzle but you did not solve the challenge ;)\n");
        return 1;
    }

    return 1;
}
*/
