There are 2 steps:

1. Figure out dictionary. This is constant between runs. See recover_dictionary.sh for a methodology to create recovered_dictionary.txt (it's not fully automated)
2. Guess the password using the dictionary and connection-specific data. See solve.py, which uses recovered_dictionary.txt (it's also not fully automated)

The .rule files come from ../src/generate_rules.py
