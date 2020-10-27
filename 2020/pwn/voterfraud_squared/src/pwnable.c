// Our words are 16-bits wide.
#define BYTES_IN_WORDS  2
#define MAGIC_START     0x6948 // Hi
#define MAGIC_END       0x7962 // yb
#define EOF 		(-1)

int putchar(int c);
int getchar(void);

// int was char
typedef int word_t;


void
puts(
    char *Str
    )
{
    for (;;)
    {
        if (*Str == '\0')
        {
            break;
        }

        putchar(*Str++);
    }
    putchar('\n');
}

char *
gets(
    char *Str
    )
{
    char *str = Str;

    for (;;)
    {
        char ch = getchar();

        if (ch == '\0' || ch == '\n')
        {
            *Str = '\0';
            break;
        }

        *Str++ = ch;
    }

    return str;
}

int
read_word(
    word_t *w
    )
{
    word_t temp;
    char buf[BYTES_IN_WORDS];
    char ch;

    temp = 0xdead;
    for (int i = 0; i < BYTES_IN_WORDS; ++i)
    {
        ch = getchar();
        if (ch == EOF)
        {
            goto Bail;
        }

        buf[BYTES_IN_WORDS - i - 1] = ch;
    }

    temp = 0;
    for (int i = 0; i < BYTES_IN_WORDS; ++i)
    {
        // shift up temp without using << or *
        if (i < BYTES_IN_WORDS - 1)
        {
            for (int j = 0; j < 256; ++j)
            {
                temp += buf[i];
            }
        }
        else
        {
            // This is the last iteration so just add it on.
            temp += buf[i];
        }
    }

Bail:
    *w = temp;
    return (ch != EOF);
}

void
go(
    void
    )
{
    word_t data[24];
    int state;
    int ok;
    int i;

    ok = read_word(&data[0]);
    if (!ok || data[0] != MAGIC_START)
    {
        return;
    }

    for (i = 0; ok; ++i)
    {
        word_t temp;
        ok = read_word(&temp);

        if (temp == MAGIC_END)
        {
            break;
        }

        data[i] = temp;
    }
}

int
main(
    void
    )
{
    char runtime_secret[32];
    char *msg;

    gets(&runtime_secret[0]);
/*
    runtime_secret[0] = 's';
    runtime_secret[1] = 'e';
    runtime_secret[2] = 'c';
    runtime_secret[3] = 'r';
    runtime_secret[4] = 'e';
    runtime_secret[5] = 't';
*/

    msg = "Premier Election Solutions Administrative Voter Correction Subchannel>>";
    puts(msg);
    go();

    msg = ">>Erroneous votes corrected. Thank you for safeguarding democracy.";
    puts(msg);

    return 0;
}
