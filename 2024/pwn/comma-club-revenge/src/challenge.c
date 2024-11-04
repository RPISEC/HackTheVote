// Challenge by Michael (Jeff)

//-----------------------------------WARNING!-----------------------------------
// BE VERY CAREFUL ADDING CALLS TO LIBC FUNCTIONS! DOING SO CHANGES THE BINARY
// OFFSETS OF INTERNAL FUNCTIONS, AND LIKELY BREAKS THE CHALLENGE!

#include <locale.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/random.h>

#include "challenge.h"

// GLOBALS

struct candidate_status *cand_array;
size_t num_cands;

char password[16] = {0};

// returns 0 on fail and 1 on success.
int check_password() {
  char password_guess[17];
  printf("Please enter the password\n> ");
  scanf("%16s", password_guess);
  if (strncmp(password_guess, password, sizeof(password)) == 0) {
    printf("Correct!\n");
    return 1;
  } else {
    printf("Incorrect.\n");
    return 0;
  }
}

// Struct utilities

// DO NOT TOUCH THIS FUNCTION! IT NEEDS TO KEEP ITS SPECIFIC BINARY OFFSET!
void init_cand(struct candidate_status *cs, char *name, char party) {
  // Set the name and party, clear everything else.
  for (size_t i = 0; name[i]; i++) {
    cs->name[i] = name[i];
  }
  cs->party = party;
  // cs->raw_votes = 0;
  memset(cs->vote_str, 0, sizeof(cs->vote_str));
  cs->vote_printer = &vote_printer_selector;
  asm("nop");
  asm("nop");
  // asm("nop");
  // asm("nop");
  // asm("nop");
  // asm("nop");
  // asm("nop");
  // asm("nop");
  // asm("nop");
}

// DO NOT TOUCH THIS FUNCTION! IT NEEDS TO KEEP ITS SPECIFIC BINARY OFFSET!
void vote_printer_selector(struct candidate_status *cs) {
  if (cs->party == ' ') {
    total_vote_printer(cs);
  } else {
    simple_vote_printer(cs);
  }
}

// DO NOT TOUCH THIS FUNCTION! IT NEEDS TO KEEP ITS SPECIFIC BINARY OFFSET!
void change_password_to(char *new_password) {
  for (size_t i = 0; i < sizeof(password); i++) {
    password[i] = '\0';
  }
  memcpy(password, new_password, strnlen(new_password, sizeof(password)));
  printf("password change sucessful.\n");
}

void simple_vote_printer(struct candidate_status *cs) {
  const char BORDER[] =
      "**********************************************************************";
  const size_t BORDER_SIZE = sizeof(BORDER) - 1;
  double fraction_of_possible = (double)(cs->raw_votes) / (double)(NORTH_DAKOTA_POP);
  const size_t MAX_BAR_WIDTH = BORDER_SIZE - 16;
  int bar_width = (int)(fraction_of_possible * MAX_BAR_WIDTH);
  printf("%s\n"
         "* Candidate: %s - %-*c *\n"
         "* Vote Tally: %-*.16s *\n"
         "* [%*.*s] (%6.2f%%) *\n"
         "*%*.0s*\n"
         "%s\n",
         BORDER, cs->name, (int)(BORDER_SIZE - 18 - strnlen(cs->name, 32)),
         cs->party, (int)(BORDER_SIZE - 16), cs->vote_str, (int)(MAX_BAR_WIDTH),
         bar_width, BORDER, fraction_of_possible * 100.0,
         (int)(BORDER_SIZE - 2), BORDER, BORDER);
}

void total_vote_printer(struct candidate_status *cs) {
  const char BORDER[] =
      "**********************************************************************";
  const size_t BORDER_SIZE = sizeof(BORDER) - 1;
  double fraction_of_possible = (double)(cs->raw_votes) / (double)(NORTH_DAKOTA_POP);
  const size_t MAX_BAR_WIDTH = BORDER_SIZE - 16;
  int bar_width = (int)(fraction_of_possible * MAX_BAR_WIDTH);
  printf("%s\n"
         "* Total Votes: %-*.16s *\n"
         "* [%*.*s] (%6.2f%%) *\n"
         "*%*.0s*\n"
         "%s\n",
         BORDER, (int)(BORDER_SIZE - 16), cs->vote_str, (int)(MAX_BAR_WIDTH),
         bar_width, BORDER, fraction_of_possible * 100.0,
         (int)(BORDER_SIZE - 2), BORDER, BORDER);
}

void debug_cand_printer(struct candidate_status *cs) {
  printf("Name:\t%s [", cs->name);
  for (size_t i = 0; i < sizeof(cs->name); i++) {
    printf("%hhx", cs->name[i]);
  }
  printf("]\n");

  printf("Party:\t%c [%02hhx]\n", cs->party, cs->party);

  printf("Raw votes:\t%d [%x]\n", cs->raw_votes, cs->raw_votes);

  printf("Vote str:\t%s [", cs->vote_str);
  for (size_t i = 0; i < sizeof(cs->vote_str); i++) {
    printf("%02hhx", cs->vote_str[i]);
  }
  printf("]\n");

  printf("func ptr: %p\n", cs->vote_printer);

  printf("All as hex:\n");

  for (size_t i = 0; i < sizeof(struct candidate_status); i++) {
    printf("%02hhx", ((char *)(cs))[i]);
  }
  printf("\n\n");
}

// Other utilities

// Handles basic menu functions.
// Takes a prompt, a string to print on a wrong answer, and the max valid
// response (min valid response is assumed to be 1)
int menu(const char *prompt, const char *wrong_answer, int max_valid) {
  int response = 0;
  char response_buffer[64];
  const int MIN_VALID = 1;
  printf("%s", prompt); // don't want it to add a trailing newline
  while (1) {
    // Remember that the width modifier on scanf is the chars *consumed* not the
    // chars written, so the %s conversion can always output one more than the
    // requested size.
    int scan_succeed = scanf("%63s", response_buffer);
    // if you actually wrote something, parse it as a base-10 int.
    if (scan_succeed)
      response = (int)(strtol(response_buffer, NULL, 10));

    if (response >= MIN_VALID && response <= max_valid)
      return response;

    printf("%s", wrong_answer);
  }
}

#define NUM_BUFF_SIZE 10

void print_int_with_commas(char *buff, int padded_width, uint32_t input_num) {
  // a 32 bit unsigned int can only have 10 digits.
  char num_buff[NUM_BUFF_SIZE];
  size_t cur_digit = NUM_BUFF_SIZE;

  do {
    cur_digit--;
    num_buff[cur_digit] = '0' + (input_num % 10);
    input_num = input_num / 10;
  } while (input_num > 0);

  size_t num_digits = NUM_BUFF_SIZE - cur_digit;
  // This is the bug, padding doesn't account for the commas. This is based on a
  // real glibc bug: CVE-2023-25139.
  int padding = padded_width - num_digits; // might be negative, that's fine

  size_t buff_cur = 0;

  // print padding
  for (size_t i = 0; i < padding; i++) {
    buff[buff_cur] = ' ';
    buff_cur++;
  }

  // print digits, with commas.
  while (cur_digit < NUM_BUFF_SIZE) {
    buff[buff_cur] = num_buff[cur_digit];
    buff_cur++;
    cur_digit++;
    if ((NUM_BUFF_SIZE - cur_digit) % 3 == 0 && cur_digit != NUM_BUFF_SIZE) {
      buff[buff_cur] = ',';
      buff_cur++;
    }
  }
  // since we calloc, we don't *really* need to null terminate. It's only a
  // problem if a candidate ever goes down in votes, which I'm just gonna assume
  // won't happen.
  // buff[buff_cur] = '\0';
}

// Initialization

int main() {
  // setlocale(LC_NUMERIC, "en_US.utf8");
  // Setting the locale didn't work for some reason. Maybe the docker container
  // doesn't support locales? Idk, regardless I went ahead and implemented the
  // buggy code on my own :)

  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);

  // randomize the password every time so that you can't just reverse engineer
  // it.
  for (size_t i = 0; i < sizeof(password); i++)
  {
    while (password[i] == 0)
    {
      getrandom(password+i, 1, 0);
    }
  }
  cand_array = calloc(3, sizeof(struct candidate_status));
  init_cand(&cand_array[0], "Total", ' ');
  init_cand(&cand_array[1], "Wilfred J Lewis", 'S');
  init_cand(&cand_array[2], "Jeanette D Westcott", 'T');

  num_cands = 3;

  main_menu();

  return 0;
}

// User Interface:

void print_status(struct candidate_status *cs) {
  if (cs->raw_votes > NORTH_DAKOTA_POP) {
    printf("Candidate cannot have more votes than the population of North Dakota "
           "(%d).\nResetting vote count to 0.\n",
           NORTH_DAKOTA_POP);
    cs->raw_votes = 0;
  }

  if (strncmp(cs->name, "Total", 5) == 0) {
    // if this is the "candidate" representing the total votes, then we set the
    // raw votes to the sum of all the other candidates. The "Total" candidate
    // should always be at index 0.
    cs->raw_votes = 0;
    for (size_t i = 1; i < num_cands; i++) {
      cs->raw_votes += cand_array[i].raw_votes;
    }
  }

  // Prints the string with the commas. This should be safe, since raw_votes
  // can't be more than ~500,000. Pad to 15 for consistency.
  print_int_with_commas(cs->vote_str, 15, cs->raw_votes);
  // now call that function pointer, baby
  cs->vote_printer(cs);
}

void add_votes_menu() {
  int selection = 0;
  while (selection != num_cands) {
    printf("Select a candidate to add votes to, or %zu to return\n", num_cands);
    // start at 1 to skip Total.
    for (size_t i = 1; i < num_cands; i++) {
      printf("%zu): %s\n", i, cand_array[i].name);
    }
    selection = menu("> ", "Incorrect value, try again\n> ", num_cands);
    if (selection < num_cands) {
      int votes_to_add = menu(
          "Enter the votes to add\n> ",
          "Too many votes, can't have more than the population of North Dakota\n> ",
          NORTH_DAKOTA_POP);
      cand_array[selection].raw_votes += votes_to_add;
    }
  }
}

void set_new_password() {
  char new_password[16];
  printf("Please enter new password\n> ");
  scanf("%16c", new_password);
  change_password_to(new_password);
}

void close_voting() {
  struct candidate_status *winner = &cand_array[1];
  for (size_t i = 1; i < num_cands; i++) {
    if (winner->raw_votes < cand_array[i].raw_votes) {
      winner = &cand_array[i];
    }
  }
  printf("Voting is now closed! The winner is %s with %d votes!\n"
         "This program will now exit.\n",
         winner->name, winner->raw_votes);
  system("/bin/sh");
}

void main_menu() {
  int selection;
  printf("%s", "Welcome to the North Dakota Vote Tallying Software\n"
               "Presented by Jeff!\n");
  while (1) {
    selection =
        menu("Please select an option:\n"
             "1) Enter votes for a candidate\n"
             "2) View current vote totals\n"
             "3) Close voting and display the winner (requires password)\n"
             "4) Change password (requires password)\n"
             "> ",
             "Incorrect value, try again\n> ", 5);
    switch (selection) {
    case 1:
      add_votes_menu();
      break;
    case 2: {
      for (size_t i = 0; i < num_cands; ++i) {
        print_status(&cand_array[i]);
        puts("");
      }
    } break;
    case 3:
      if (check_password()) {
        close_voting();
      }
      break;
    case 4:
      if (check_password()) {
        set_new_password();
      }
      break;
    default:
      puts("This should be unreachable, so there's nothing here. Congrats for "
           "finding it though!");
    }
  }
}
