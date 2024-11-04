# Comma Club
## By Michael "Jeff" Jones

We need somone to run our vote tallying machine, and it needs to be someone
trustworthy. Apparently there's some problem if a candidate gets too many votes.
Shouldn't be a problem for us in Wyoming though.

### WARNING: Spoilers ahead

<details>
  <summary>For Maintainers</summary>

IMPORTANT: Don't add or remove code before "change_password_to", and don't add
or remove libc calls. Both of these may make the challenge unsolvable. For
details, read on.

This challenge is based on a fairly simply buffer overflow via an incorrect
bounds check. The bug is in "print_int_with_commas" which attempts to pad the
string containing the number of votes, as well as adding commas (similar to
"%*'d"). Each comma overwrites one byte beyond the end of the string. The code
will work correctly with 1 comma (it overwrites the null terminator, but the 
printf %s is limited to not show it), but with 2 commas it overwrites the last
byte of the "vote_printer" function pointer in "candadite_status". It's
impossible to add more than ~500,000 votes to any one candidate (the population
of Wyoming), but there's a secret extra candidate named "Total" that adds up the
votes of every other candidate, meaning if both the real candidates get over
500,000 votes it overflows to 1,000,000. The overflow writes the last digit of
the number as the last byte of the function pointer, so the challenge only works
if the start of "change_password_to" has a last byte that is an ascii digit
(0x30-0x39), and the pointer for "vote_printer_selector" is the same except for
the last byte. That's why the offsets matter so much, getting those to line up
is a pain. That's also why there's a bunch of "nop"s at the end of "init_cand",
so I can force the offset.

Overall this challenge is pretty easy, but it's also based on a real CVE
(CVE-2023-25139) so I think it's neat.
</details>