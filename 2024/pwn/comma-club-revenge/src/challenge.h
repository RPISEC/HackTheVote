// Challenge by Michael (Jeff)

#include <stdint.h>

// as of the 2023 census
const int NORTH_DAKOTA_POP = 783926;

struct candidate_status {
  char name[32];
  char party;
  int raw_votes;
  // gee I hope nobody overflows vote_str into that function pointer
  char vote_str[16];
  void (*vote_printer)(struct candidate_status *);
};

void init_cand(struct candidate_status *, char *name, char party);
int menu(const char *prompt, const char *wrong_answer, int max_valid);
void main_menu();
void print_int_with_commas(char *buff, int padded_width, uint32_t input_num);
void print_status(struct candidate_status *cs);
void change_password_to(char *new_password);

void vote_printer_selector(struct candidate_status *cs);
void simple_vote_printer(struct candidate_status *cs);
void total_vote_printer(struct candidate_status *cs);
void debug_cand_printer(struct candidate_status *cs);

int check_password();

void close_voting();
void set_new_password();
