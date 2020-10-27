#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>


char* string_guard = "__string_guard";
const size_t num_topics = 5;
char* topic_names[] = {
    "Our Right to be Stoked, dude",
    "Are memes absolutely a waste of time",
    "Is PIE a misleading name because its not actually pie?",
    "Boneless Chicken Wings",
    "Is CFG Infringing on our 50th amendment rights to execute?",
};

const size_t topic_answer_lens[] = { 3, 1, 2, 2, 2 };

char* topic_answers[5][3] = {
    {
        "Dude, we've gotta stay stoked, #protectstoke",
        "Stoke is a national security threat",
        "We need to preserve our right to stoke, but make sure it stays in the right hands",
    },
    {
        "Yes",
        NULL,
        NULL,
    },
    {
        "No, what idiot doesn't know it stands for 'Performance, Image and Exposure'",
        "Yes, whenever i think about it i just want real PIE and then get really sad cause i dont have any pie on me",
        NULL,
    },
    {
        "Boneless chicken wings ARE NOT CHICKEN WINGS",
        "Who cares, i just want chicken",
        NULL,
    },
    {
        "Our founding AI stated that we are allowed to execute ANYTHING WE WANT, AND GOSH DARN IT, WE WILL STAND BY IT",
        "When our founding AI stated that we were allowed to execute anything, they were living in a different time.  They were dealing with some amateur coders, not shellcode and ROPchains.  We need to modernize, and limit our execution.",
        NULL,
    }
};

const size_t num_candidates = 5;
char* blue_candidate_names[] = {
    "Cyber Lincoln",
    "Mecha 'Mechinridge' Breckinridge",
    "HamlinBot",
    "'Wired Willy' William Seward 19.0.45",
    "John RoboBell",
};
char* yellow_candidate_names[] = {
    "Cyber Washington",
    "Johns[0] #[AKA. AT0M5]",
    "Johns[1] #[AKA. Jay]",
    "Johns[2] #[AKA. Rutledge]",
    "Johns[3] #[AKA. Hancock]",
};
char* yellow_convension = "yellow national convention";
char* blue_convension = "blue national convention";

char* buffer[12] = { "" };

const size_t num_states = 8;
char* states[] = {
    "new york()",
    "delete york",
    "ASLRkensaw",
    "CFGeorgia",
    "tech sas",
    "ca11f0rn14",
    "malloc(jersey)",
    "int maine(){return 0}",
};

char* string_guard_end = "__string_guard_end";

void safe_write(char* string) {
    if (string >= string_guard && string < string_guard_end) {
        printf("%s", string);
    }
}

struct _Convension;

typedef struct _Candidate {
    char* name;
    char* home_state;
    size_t votes;
    size_t other_candidate;
    char* victory_speech;
    struct _Convension* convension;

    char* positions[];
} Candidate;

typedef struct _Convension {
    char* name;
    Candidate* candidates;
    Candidate* nominee;
    size_t current_state;
} Convension;

Convension BLUE_CONVENSION;
Convension YELLOW_CONVENSION;

void add_candidate(Candidate* a, Candidate* b) {
    a->other_candidate = (size_t)b;
    if (b != NULL) {
        b->other_candidate ^= (size_t)a;
    }
}

Candidate* new_candidate(char* name, char** positions, Candidate* other_candidate) {
    Candidate* c = (Candidate*)malloc(sizeof(Candidate) + (sizeof(char*) * num_topics));
    c->name = name;
    c->votes = 0;
    c->home_state = states[(rand() % num_states)];
    c->convension = NULL;
    for (size_t i = 0; i < num_topics; ++i) {
        c->positions[i] = positions[i];
    }

    add_candidate(c, other_candidate);
    return c;
}

Candidate* remove_candidate(Candidate* target, Candidate* neighbor) {
    Candidate* other_neighbor = (Candidate*)(target->other_candidate ^ (size_t)neighbor);

    if (other_neighbor != NULL) {
        other_neighbor->other_candidate ^= (size_t)target ^ (size_t)neighbor;
    }

    if (neighbor != NULL) {
        neighbor->other_candidate ^= (size_t)target ^ (size_t)other_neighbor;
    }

    return target;
}

void delete_candidate(Candidate* target, Candidate* neighbor) {
    free(remove_candidate(target, neighbor));
}

typedef struct _CandidateIterator {
    Candidate* previous;
    Candidate* current;
    size_t index;
} CandidateIterator;

void init_candidate_iterator(CandidateIterator* it, Candidate* start) {
    it->previous = NULL;
    it->current = start;
    it->index = 0;
}

CandidateIterator* candidate_iterator(Candidate* start) {
    CandidateIterator* new = (CandidateIterator*)malloc(sizeof(CandidateIterator));
    init_candidate_iterator(new, start);
    return new;
}

Candidate* step_candidate_iterator(CandidateIterator* it) {
    if (it->current != NULL) {
        Candidate* previous = it->previous;
        it->previous = it->current;
        Candidate* current = it->current;
        ++it->index;
        it->current = (Candidate*)(it->current->other_candidate ^ (size_t)previous);

        return current;
    } else {
        return NULL;
    }
}

int end_finished_iterator(CandidateIterator* it) {
    if (it->current == NULL) {
        free(it);
        return 1;
    } else {
        return 0;
    }
}

Candidate* get_candidate_by_index(Candidate* head, size_t i) {
    for(CandidateIterator* it = candidate_iterator(head); !end_finished_iterator(it); step_candidate_iterator(it), --i) {
        if (i == 0) {
            return it->current;
        }
    }

    exit(-1);
}

void delete_all_candidates(Candidate* head) {
    CandidateIterator* it;
    for(it = candidate_iterator(head); it->current != NULL; step_candidate_iterator(it)) {
        if (it->previous != NULL) {
           free((Candidate*)it->previous);
        }
    }

    free((Candidate*)it->previous);
}

size_t get_int() {
    char buffer[32];
    if (read(0, buffer, 32) == -1) {
        exit(-1);
    }

    return (size_t)atol(buffer);
}

void view_candidates(Candidate* candidates);

Candidate* get_candidate(Candidate* head, char* prompt) {
    view_candidates(head);
    puts(prompt);
    size_t i = get_int();
    return get_candidate_by_index(head, i);
}

void pretty_print(char* pre, char* safe, char* post) {
    printf("%s", pre);
    safe_write(safe);
    if (post != NULL) {
        puts(post);
    }
}

/*
[1] view candidates
[2] question candidate
[3] vote
[5] rig election ;)
[6] drop out
[7] verify candidate
 */

void view_candidates(Candidate* candidates) {
    if (BLUE_CONVENSION.nominee == NULL || YELLOW_CONVENSION.nominee == NULL) {
        puts("Candidates:\n");
        for(CandidateIterator* i = candidate_iterator(candidates); !end_finished_iterator(i); step_candidate_iterator(i)) {
            safe_write(i->current->name);
            pretty_print(" from ", i->current->home_state, "");
        }
        puts("");
    } else {
        puts("Nominees:");
        pretty_print("Representing the blue party: ", candidates->name, "");
        pretty_print("Representing the yellow party: ", ((Candidate*)candidates->other_candidate)->name, "\n");
    }
}

void view_topics() {
    puts("Topics:\n");
    for (size_t i = 0; i < num_topics; ++i) {
        safe_write(topic_names[i]);
        puts("");
    }
    puts("");
}

void question_candidate(Candidate* candidates) {
    Candidate* c = get_candidate(candidates, "which candidate would you like to question? [enter number, 0-indexed of course ;)]");
    pretty_print("which topic would you like to question ", c->name, " on?");
    view_topics(candidates);
    size_t j = get_int();
    if (j >= num_topics) {
        exit(-1);
    }
    pretty_print("\"", c->positions[j], "\"");
    pretty_print("\t- ", c->name, "");
}

void choose_nominee(Convension* convension) {
    Candidate* nominee = NULL;
    Candidate* nominee_neighbor = NULL;
    for (CandidateIterator* i = candidate_iterator(convension->candidates); !end_finished_iterator(i); step_candidate_iterator(i)) {
        if (nominee == NULL || i->current->votes > nominee->votes) {
            nominee = i->current;
            nominee_neighbor = i->previous;
        }
    }

    puts("");
    safe_write(convension->name);
    pretty_print(" has chose ", nominee->name, "\n");

    if (nominee == convension->candidates) {
        convension->candidates = (Candidate*)nominee->other_candidate;
    }
    convension->nominee = remove_candidate(nominee, nominee_neighbor);
}

void vote(Convension* convension) {
    pretty_print("holding ", convension->name, NULL);
    pretty_print(" for ", states[convension->current_state], "");

    Candidate* c = get_candidate(convension->candidates, "which candidate would you like to vote for?");
    ++c->votes;
    ++convension->current_state;
    puts("your vote has been counted!  we promise :)");
    choose_nominee(convension);
}

void drop_out(Candidate** candidates_ptr) {
    Candidate* c = get_candidate(*candidates_ptr, "which candidate should drop out?");
    char* name = c->name;

    if (c == *candidates_ptr) {
        *candidates_ptr = (Candidate*)c->other_candidate;
        delete_candidate(c, NULL);
    } else {
        for (CandidateIterator* i = candidate_iterator(*candidates_ptr); !end_finished_iterator(i); step_candidate_iterator(i)) {
            if (i->current == c) {
                delete_candidate(i->current, i->previous);
                break;
            }
        }
    }
    pretty_print("", name, " has dropped out of the race!");
}

void write_victory_speech(Candidate* nominees) {
    Candidate* nominee = get_candidate(nominees, "Its never too early to plan for victory!  Which nominee would you like to prepare a victory speech for?");
    puts("How long is the speech?");
    size_t speech_length = get_int();
    if (speech_length < 2) {
        exit(-1);
    }
    nominee->victory_speech = (char*)malloc(speech_length);

    int num_bytes = read(0, nominee->victory_speech, speech_length);
    if (num_bytes == -1) {
        exit(-1);
    } else {
        nominee->victory_speech[num_bytes - 1] = 0x0;
    }
    puts("We have recorded your victory speech!");
}

void convension_menu(Convension* convension) {
    if (convension->candidates == NULL) {
        exit(-1);
    }

    puts("");
    pretty_print("welcome to the ", convension->name, "");
    pretty_print("currently holding the ", states[convension->current_state], " primaries");

    puts(
        "[0] view candidates\n"
        "[1] question candidate\n"
        "[2] vote\n"
        "[3] drop out\n"
    );
    printf("choice: ");
    switch (get_int()) {
        case 0:
            view_candidates(convension->candidates);
            break;
        case 1:
            question_candidate(convension->candidates);
            break;
        case 2:
            vote(convension);
            break;
        case 3:
            drop_out(&convension->candidates);
            break;
        default:
            puts("invalid option");
    }
}

Candidate* create_candidate_list(char** candidate_names, Convension* convension) {
    Candidate* head = NULL;
    char* positions[num_topics];

    for (size_t i = 0; i < num_candidates; ++i) {
        for (size_t j = 0; j < num_topics; ++j) {
            positions[j] = topic_answers[j][rand() % topic_answer_lens[j]];
        }
        head = new_candidate(candidate_names[i], positions, head);
        head->convension = convension;
    }

    return head;
}

void elect_nominees() {
    while (1) {
        if (BLUE_CONVENSION.nominee == NULL) {
            puts("[0] to visit blue convention");
        }
        if (YELLOW_CONVENSION.nominee == NULL) {
            puts("[1] to visit yellow convention");
        }

        size_t i = get_int();

        if (BLUE_CONVENSION.nominee == NULL && i == 0) {
            convension_menu(&BLUE_CONVENSION);
        } else if (YELLOW_CONVENSION.nominee == NULL && i == 1) {
            convension_menu(&YELLOW_CONVENSION);
        } else {
            puts("invalid choice");
        }

        if (BLUE_CONVENSION.nominee != NULL && YELLOW_CONVENSION.nominee != NULL) {
            puts("#######################\nthe primaries are over!\n#######################");
            break;
        }
    }
}

void nominees_menu() {
    Candidate* nominees = BLUE_CONVENSION.nominee;
    add_candidate(nominees, YELLOW_CONVENSION.nominee);

    delete_all_candidates(BLUE_CONVENSION.candidates);
    BLUE_CONVENSION.candidates = NULL;
    delete_all_candidates(YELLOW_CONVENSION.candidates);
    YELLOW_CONVENSION.candidates = NULL;

    puts("#######################\nwe are ready for the presidential election now!\n#######################");
    view_candidates(nominees);
    while (1) {
        puts(
            "[0] view candidates\n"
            "[1] question candidate\n"
            "[2] drop out\n"
            "[3] write a pre-mature victory speech\n"
            "[4] exit\n"
        );
        printf("choice: ");
        switch (get_int()) {
            case 0:
                view_candidates(nominees);
                break;
            case 1:
                question_candidate(nominees);
                break;
            case 2:
                drop_out(&nominees);
                break;
            case 3:
                write_victory_speech(nominees);
                break;
            case 4:
                exit(0);
            default: 
                puts("Invalid choice");
        }
    }
}

int main(void) {
    setvbuf(stdin, 0, _IONBF, 0);
    setvbuf(stdout, 0, _IONBF, 0);

    BLUE_CONVENSION.name = blue_convension;
    BLUE_CONVENSION.candidates = create_candidate_list(blue_candidate_names, &BLUE_CONVENSION);
    
    BLUE_CONVENSION.nominee = NULL;
    BLUE_CONVENSION.current_state = 0;

    YELLOW_CONVENSION.name = yellow_convension;
    YELLOW_CONVENSION.candidates = create_candidate_list(yellow_candidate_names, &YELLOW_CONVENSION);
    YELLOW_CONVENSION.nominee = NULL;
    YELLOW_CONVENSION.current_state = 0;

    elect_nominees();
    nominees_menu();
}
