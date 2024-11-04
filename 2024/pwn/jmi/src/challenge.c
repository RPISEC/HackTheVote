#include <errno.h>
#include <signal.h>
#include <string.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>


#define PROGRAM_SIZE 0x1000
#define MAX_BYTECODE_INSTRUCTIONS 0x1000

#define NATIVE_CODE_BLOCK_SIZE 65
#define NATIVE_CODE_SIZE MAX_BYTECODE_INSTRUCTIONS * NATIVE_CODE_BLOCK_SIZE

#define P32(x) (x & 0xff), ((x >> 8) & 0xff), ((x >> 16) & 0xff), ((x >> 24) & 0xff)
#define P64(x) (x & 0xff), ((x >> 8) & 0xff), ((x >> 16) & 0xff), ((x >> 24) & 0xff), ((x >> 32) & 0xff), ((x >> 40) & 0xff), ((x >> 48) & 0xff), ((x >> 56) & 0xff)


#define OP_ADD 1
#define OP_PRINT 2
#define OP_IF 3
#define OP_NATIVE_CODE 4


typedef struct bytecode_op {
    uint8_t operation;
    uint64_t operand;
} bytecode_op;


typedef struct label {
    char* name;
    uint32_t native_code_offset;
    uint32_t bytecode_offset;
    struct label* next;
} label;


char* PROGRAM;
bytecode_op* BYTECODE;
char* NATIVE_CODE;
char* DATA;

label* LABEL_HEAD = NULL;

size_t BYTECODE_INSN_COUNT = 0;
size_t NATIVE_CODE_LEN = 0;

uint64_t REGISTER = 0;
uint8_t IN_IF = 0;

label* find_label(char* name)
{
    label* curr = LABEL_HEAD;
    while (curr)
    {
        if (strcmp(curr->name, name) == 0)
        {
            return curr;
        }
        curr = curr->next;
    }
    return NULL;
}


void do_add(uint64_t num)
{
    REGISTER += num;
}


void do_print()
{
    printf("%lu\n", REGISTER);
}


char check_not_zero()
{
    return REGISTER != 0;
}


int parse_line(char* line, int parse_only)
{
    // Returns the number of bytecode instructions parsed from the line
    if (BYTECODE_INSN_COUNT > MAX_BYTECODE_INSTRUCTIONS)
    {
        printf("bytecode too long: %lu vs %d\n", BYTECODE_INSN_COUNT, MAX_BYTECODE_INSTRUCTIONS);
        return 0;
    }
    char* state;
    char* operation = strtok_r(line, " ", &state);
    if (operation == NULL)
    {
        puts("Missing operation");
        return 0;
    }

    // Optional operand, checked by each instruction
    char* operand = strtok_r(NULL, " ", &state);

    bytecode_op bytecode = {0};

    if (!strcmp(operation, "ADD"))
    {
        if (operand == NULL)
        {
            puts("Parse error: ADD missing operand");
            exit(1);
        }

        uint64_t val = strtoul(operand, NULL, 10);
        if (errno == ERANGE || errno == EINVAL)
        {
            puts("Parse error: Invalid ADD operand value");
            exit(1);
        }

        bytecode.operation = OP_ADD;
        bytecode.operand = val;
    }
    else if (!strcmp(operation, "PRINT"))
    {
        if (operand != NULL)
        {
            puts("Parse error: PRINT does not take operand");
            exit(1);
        }
        bytecode.operation = OP_PRINT;
    }
    else if (!strcmp(operation, "TIMES"))
    {
        if (operand == NULL)
        {
            puts("Parse error: TIMES missing operand");
            exit(1);
        }

        uint64_t val = strtoul(operand, NULL, 10);
        if (errno == ERANGE || val == 0 || val >= 100)
        {
            puts("Parse error: Invalid TIMES operand value");
            exit(1);
        }

        int num_insns = 0;
        for (size_t i = 0; i < val && BYTECODE_INSN_COUNT < MAX_BYTECODE_INSTRUCTIONS; i++)
        {
            char* inner_contents_copy = strdup(line + strlen(operation) + strlen(operand) + 2);
            if (inner_contents_copy == NULL)
            {
                puts("strdup error");
                exit(1);
            }
            num_insns += parse_line(inner_contents_copy, parse_only);
            free(inner_contents_copy);
        }
        return num_insns;
    }
    else if (!strcmp(operation, "IF"))
    {
        if (operand != NULL)
        {
            puts("Parse error: IF does not take operand");
            exit(1);
        }

        if (IN_IF)
        {
            puts("Parse error: Nested IF not allowed");
            exit(1);
        }
        // Count number of instructions inside the IF until ENDIF
        size_t num_insns = 0;
        IN_IF = 1;

        char* code_after = strdup(line + strlen(operation) + 1);
        char* saveptr;
        char* next_line = strtok_r(code_after, "\n", &saveptr);
        while (next_line != NULL && strcmp(next_line, "ENDIF") != 0)
        {
            // Parse the next line
            num_insns += parse_line(next_line, 1);
            // look forward until endif or end of input
            // if end of input reached without endif, parse error
            next_line = strtok_r(NULL, "\n", &saveptr);
        }
        free(code_after);

        bytecode.operation = OP_IF;
        bytecode.operand = num_insns;
    }
    else if (!strcmp(operation, "ENDIF"))
    {
        if (operand != NULL)
        {
            puts("Parse error: ENDIF does not take operand");
            exit(1);
        }

        if (!IN_IF)
        {
            puts("Parse error: ENDIF without IF");
            exit(1);
        }

        IN_IF = 0;
        return 0;
    }
    else
    {
        puts("Parse Error: Unknown instruction");
        exit(1);
    }

    if (!parse_only)
        BYTECODE[BYTECODE_INSN_COUNT++] = bytecode;

    return 1;
}


void compile_instruction(bytecode_op* op)
{
    char* code_dest = NATIVE_CODE + NATIVE_CODE_LEN;

    char code[NATIVE_CODE_BLOCK_SIZE];
    memset(code, 0x90, sizeof(code));

    switch (op->operation)
    {
        case OP_ADD:
        {
            /*
                mov rdi, <const 64>
                movabs rax, &do_add
                call rax
            */
            char add_code[] = {'\x48', '\xbf', P64(op->operand),
            '\x48', '\xb8', P64(((uint64_t)&do_add)),
            '\xff', '\xd0',
            };
            memcpy(code, add_code, sizeof(add_code));
            break;
        }
        case OP_PRINT:
        {
            /*
                movabs rax, &add_num
                call rax
            */
            char print_code[] = {
            '\x48', '\xb8', P64(((uint64_t)&do_print)),
            '\xff', '\xd0',
            };
            memcpy(code, print_code, sizeof(print_code));
            break;
        }
        case OP_IF:
        {
            /*
                movabs rax, &check_not_zero
                call rax
                test rax, rax
                jz <num bytes forward>
            */
            uint32_t num_bytes_to_jump = (NATIVE_CODE_BLOCK_SIZE * op->operand) + NATIVE_CODE_BLOCK_SIZE - 21; // -21 because it's relative to end of the instruction, add block because we skip the rets
            //printf("Native if skipping %d bytes\n", num_bytes_to_jump);
            char jump_code[] = {
            '\x48', '\xb8', P64(((uint64_t)&check_not_zero)),
            '\xff', '\xd0',
            '\x48', '\x85', '\xc0',
            '\x0f', '\x84', P32(num_bytes_to_jump),
            };

            memcpy(code, jump_code, sizeof(jump_code));
            break;
        }
        default:
            puts("Invalid bytecode");
            return;
    }

    if (NATIVE_CODE_LEN + sizeof(code) > NATIVE_CODE_SIZE)
    {
        puts("Native code too long");
        return;
    }

    memcpy(code_dest, code, sizeof(code));
    op->operation = OP_NATIVE_CODE;
    op->operand = NATIVE_CODE_LEN;
    NATIVE_CODE_LEN += sizeof(code);
}


void execute_bytecode_instruction(bytecode_op* op, uint8_t compile_only)
{
    // returns number of instructions to step forward
    if (!compile_only)
    {
        switch (op->operation)
        {
            case OP_ADD:
                do_add(op->operand);
                break;
            case OP_PRINT:
                do_print();
                break;
            case OP_NATIVE_CODE:
            {
                void (*target)(void) = (void*)(NATIVE_CODE + op->operand);
                target();
                return;
            }
            case OP_IF:
            {
                break;
            }
            default:
                printf("Invalid bytecode %hhu\n", op->operation);
                break;
        }
    }
    // compile write native code and replace bytecode instruction with OP_NATIVE_CODE <offset>
    compile_instruction(op);
    return;
}


void run_bytecode()
{
    REGISTER = 0;
    size_t to_skip = 0;
    for (size_t i = 0; i < BYTECODE_INSN_COUNT; i++)
    {
        bytecode_op op_copy = BYTECODE[i];
        bytecode_op* op = &BYTECODE[i];
        if (op->operation == OP_IF && REGISTER == 0)
        {
            to_skip = op->operand;
            //printf("Skipping %lu...\n", to_skip);
        }

        execute_bytecode_instruction(op, to_skip > 0);
        if (to_skip > 0)
        {
            if (op_copy.operation != OP_IF)
                to_skip--;
        }
    }
}


void handle_alarm()
{
    kill(0, SIGKILL);
}


int main()
{
    signal(SIGALRM, handle_alarm);
    alarm(15);

    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    PROGRAM = malloc(PROGRAM_SIZE+1);
    memset(PROGRAM, 0, PROGRAM_SIZE+1);

    BYTECODE = malloc(MAX_BYTECODE_INSTRUCTIONS*sizeof(bytecode_op));
    memset(BYTECODE, 0, MAX_BYTECODE_INSTRUCTIONS*sizeof(bytecode_op));

    NATIVE_CODE = aligned_alloc(0x1000, NATIVE_CODE_SIZE);
    memset(NATIVE_CODE, 0xc3, NATIVE_CODE_SIZE);

    if (mprotect(NATIVE_CODE, NATIVE_CODE_SIZE, PROT_READ|PROT_WRITE|PROT_EXEC) != 0)
    {
        puts("mprotect error, contact an admin.");
        exit(1);
    }

    printf("Code: ");
    if (read(0, PROGRAM, PROGRAM_SIZE) == -1)
    {
        puts("Read failed");
        exit(1);
    }

    char* saveptr;
    char* line = strtok_r(PROGRAM, "\n", &saveptr);
    while (line)
    {
        if (BYTECODE_INSN_COUNT >= MAX_BYTECODE_INSTRUCTIONS)
        {
            puts("Bytecode too long!");
            break;
        }

        parse_line(line, 0);

        line = strtok_r(NULL, "\n", &saveptr);
    }

    run_bytecode();

    REGISTER = 0;
    void (*target)(void) = (void*)(NATIVE_CODE);
    target();

    return 0;
}
