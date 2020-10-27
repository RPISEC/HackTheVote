#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdarg.h>
#include <unistd.h>
#include "alphabet.h"

char *username = "ADMIN";
char *password = "FARMFORLYFE";
char **dictionary;
int num_words;

void cowsay(const char *format, ...){
    char s[1024];
    va_list args;
    va_start(args, format);
    vsnprintf(s, sizeof(s), format, args);
    va_end(args);

    int len = strlen(s);
    if (s[len - 1] == '\n'){
        s[len - 1] = '\0';
        len--;
    }
    int count = 0;
    int max_len = 0;
    for (int i = 0; i < len; i++){
        count++;
        if (s[i] == '\n' || i == len - 1){
            if (count > max_len){
                max_len = count;
            }
            count = 0;
        }
    }
    if (max_len == 0) max_len = len;
    char *token = NULL;
    char *rest = s;
    printf(" ");
    for (int i = 0; i < max_len + 2; i++) printf("_");
    printf("\n");
    while ((token = strtok_r(rest, "\n", &rest))){
        printf("( %s", token);
        for (int i = 0; i <= max_len - strlen(token); i++) printf(" ");
        printf(")\n");
    }
    printf(" ");
    for (int i = 0; i < max_len + 2; i++) printf("‾");
    printf("\n");
    printf("        \\   ^__^\n");
    printf("         \\  (oo)\\_______\n");
    printf("            (__)\\       )\\/\\\n");
    printf("                ||----w |\n");
    printf("                ||     ||\n");
}

void to_upper(char *s){
    for (int i = 0; i < strlen(s); i++){
        if (s[i] >= 'a' && s[i] <= 'z'){
            s[i] -= 32;
        }
    }
}

bool all_alpha(char *s){
    for (int i = 0; i < strlen(s); i++){
        if (!isalpha(s[i])){
            return false;
        }
    }
    return true;
}

int read_dictionary(char **dictionary){
    FILE *fp = fopen("dict", "r");
    if (!fp) return -1;

    char *line = NULL;
    size_t len = 0;

    int i = 0;
    while(getline(&line, &len, fp) != -1){
        line[strcspn(line, "\n")] = '\0';
        len = strlen(line);
        if (len < 3) continue;
        if (!all_alpha(line)) continue;
        to_upper(line);
        dictionary[i] = malloc(len + 1);
        strcpy(dictionary[i], line);
        i++;
    }
    fclose(fp);
    free(line);
    return i;
}

bool in_dictionary(char *s, char **dictionary, int num_words){
    int low = 0;
    int high = num_words;
    while (low <= high){
        int mid = low + ((high - low) / 2);
        int cmp = strcmp(s, dictionary[mid]);
        if (cmp == 0) return true;
        else if (cmp > 0) low = mid + 1;
        else high = mid - 1;
    }
    return false;
}

bool verify_input(char *input[12], int len, char **dictionary, int num_words){
    char *s = malloc(len + 1);
    char *text[1024] = {NULL};
    char *token = NULL;
    char *rest = NULL;
    bool valid = true;
    int idx = 0;
    for (int i = 0; i < 12 && valid; i++){
        strcpy(s, input[i]);
        rest = s;
        while(valid && (token = strtok_r(rest, " ", &rest))){
            to_upper(token);
            if (!in_dictionary(token, dictionary, num_words)){
                valid = false;
            }
            text[idx] = malloc(strlen(token) + 1);
            strcpy(text[idx], token);
            idx++;
        }
    }
    for (int i = 0; text[i] && valid; i++){
        for (int j = i + 1; text[j] && valid; j++){
            if (strcmp(text[i], text[j]) == 0){
                valid = false;
            }
        }
    }
    free(s);
    for (int i = 0; text[i]; i++){
        free(text[i]);
    }
    return valid;
}

bool has_holes(char c){
    return (c == 'A' || c == 'B' || c == 'D' || c == 'O' || c == 'P' || c == 'Q' || c == 'R');
}

bool match_letter(int l[12][12], int idx){
    for (int i = 0; i < 12; i++){
        for (int j = 0; j < 12; j++){
            if (l[i][j] == 2) continue;
            bool bit = (letters[idx][i] >> (11 - j)) & 0x1;
            if (bit != l[i][j]) return false;
        }
    }
    return true;
}

char decode_letter(int letter[12][12]){
    char c = '*';
    for (int i = 0; i < 27; i++){
        if (match_letter(letter, i)){
            c = alphabet[i];
            break;
        }
    }
    return c;
}

char *decode_input(char *input[12], int max_len, char *passphrase){
    int len = strlen(passphrase);
    char *ret = calloc(len + 1, sizeof(char));
    for (int i = 0; i < len; i++){
        int letter[12][12] = {0};
        for (int j = 0; j < 12; j++){
            int num_spaces = 0;
            int segment_length = 0;
            bool in_segment = false;
            for (int k = 0; k < 5; k++){
                if (has_holes(input[j][k])){
                    return NULL;
                }
            }
            int bound = 16;
            if (i == len - 1) bound++;
            for (int k = 0; k < bound; k++){
                char c0 = input[j][5 + 16*i + k];
                if (k < 12){
                    char c1 = input[j][6 + 16*i + k];
                    if (has_holes(c0)){
                        letter[j][k] = 1;
                        in_segment = true;
                        segment_length++;
                    } else if (has_holes(c1)){
                        if (c0 == ' ' && num_spaces < 2 && in_segment){
                            num_spaces++;
                            letter[j][k] = 2;
                        }
                    } else {
                        in_segment = false;
                        if (0 < segment_length && segment_length <= 4 && num_spaces != 0){
                            return NULL;
                        }
                        segment_length = 0;
                    }
                } else {
                    if (has_holes(c0)){
                        return NULL;
                    }
                }
            }
        }
        ret[i] = decode_letter(letter);
    }
    return ret;
}

bool read_passphrase(char *passphrase){
    bool valid_passphrase = false;
    bool valid_len = true;
    char *input[12] = {NULL};
    int max_len = 16*strlen(passphrase) + 6;
    for (int i = 0; i < 12; i++){
        input[i] = malloc(max_len + 2);
        char *line = input[i];
        printf("> ");
        fgets(line, max_len + 2, stdin);
        line[strcspn(line, "\n")] = '\0';
        if (strlen(line) != max_len){
            valid_len = false;
            break;
        }
    }
    printf("\n");
    if (valid_len){
        bool valid_input = verify_input(input, max_len, dictionary, num_words);
        if (valid_input){
            char *output = decode_input(input, max_len, passphrase);
            if (output){
                if (strcmp(output, passphrase) == 0){
                    valid_passphrase = true;
                } else {
                    cowsay("Wrong!");
                }
            } else {
                cowsay("Invalid input!");
            }
            free(output);
        } else {
            cowsay("Invalid input!");
        }
    } else {
        cowsay("Invalid input!");
    }

    for (int i = 0; i < 12; i++){
        free(input[i]);
    }
    return valid_passphrase;
}

int main(){
    dictionary = calloc(123115, sizeof(char *));
    num_words = read_dictionary(dictionary);

    if (num_words > 0){
        cowsay("Welcome to the IoTractor Firmware Remote Update Utility.\nPlease provide your login credentials, in the correct format.");
        printf("USERNAME:\n");
        if (read_passphrase(username)){
            printf("PASSWORD:\n");
            if (read_passphrase(password)){
                char flag[64] = {0};
                FILE *fp = fopen("flag.txt", "r");
                if (fp){
                    fgets(flag, sizeof(flag), fp);
                    cowsay("Access granted! %s", flag);
                    fclose(fp);
                } else {
                    char cwd[128];
                    getcwd(cwd, sizeof(cwd));
                    cowsay("flag.txt doesn't exist in %s!", cwd);
                }
            }
        }
        for (int i = 0; i < num_words; i++){
            free(dictionary[i]);
        }
    } else {
        cowsay("Dict not found!");
    }
    free(dictionary);
    return 0;
}
