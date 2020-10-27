import enum
import itertools
import secrets
import string


class ArgType(enum.Enum):
    POS = enum.auto()
    ANYCHAR = enum.auto()
    WORDCHAR = enum.auto()
    COUNT = enum.auto()


CHARS = string.ascii_letters + string.digits + string.punctuation

RULES = (
    (':'),
    ('l'),
    ('l'),
    ('u'),
    ('c'),
    ('C'),
    ('t'),
    ('r'),
    ('d'),
    ('f'),
    ('['),
    (']'),
    ('{'),
    ('}'),
    ('k'),
    ('K'),
    ('q'),
    ('E'),
    ('T', ArgType.POS),
    ('D', ArgType.POS),
    ("'", ArgType.POS),
    ('+', ArgType.POS),
    ('-', ArgType.POS),
    ('L', ArgType.POS),
    ('R', ArgType.POS),
    ('.', ArgType.POS),
    (',', ArgType.POS),
    ('p', ArgType.COUNT),
    ('z', ArgType.COUNT),
    ('Z', ArgType.COUNT),
    ('y', ArgType.COUNT),
    ('Y', ArgType.COUNT),
    ('$', ArgType.ANYCHAR),
    ('^', ArgType.ANYCHAR),
    ('@', ArgType.WORDCHAR),
    ('s', ArgType.WORDCHAR, ArgType.ANYCHAR),
    ('i', ArgType.POS, ArgType.ANYCHAR),
    ('o', ArgType.POS, ArgType.ANYCHAR),
    ('*', ArgType.POS, ArgType.POS),
    ('O', ArgType.POS, ArgType.COUNT),
    ('x', ArgType.POS, ArgType.COUNT),
)

def int2pos(i):
    if i < 0:
        raise ValueError(f'position needs to be non-negative: {i}')
    if i < 10:
        return str(i)
    if 0 < i < 36:
        return chr(0x40 + i)
    raise ValueError(f'position needs to be < 36: {i}')

def generate_random_rule(word_length_max=15, max_count=5):
    positions = [int2pos(x) for x in range(word_length_max)]
    rule = secrets.choice(RULES)
    rule_buf = rule[0]
    for arg in rule[1:]:
        if arg == ArgType.POS:
            rule_buf += secrets.choice(positions)
        elif arg == ArgType.ANYCHAR:
            rule_buf += secrets.choice(CHARS)
        elif arg == ArgType.WORDCHAR:
            rule_buf += secrets.choice(string.ascii_lowercase)
        elif arg == ArgType.COUNT:
            rule_buf += str(1 + secrets.randbelow(max_count - 1))
    return rule_buf

def generate_all_rules(word_length_max=15, max_count=5):
    positions = [f'{x:X}' for x in range(word_length_max)]
    for rule in RULES:
        if rule[0] == ':':
            continue
        rule_possibilites = [rule[0], ]
        for arg in rule[1:]:
            if arg == ArgType.POS:
                rule_possibilites.append(positions)
            elif arg == ArgType.ANYCHAR:
                rule_possibilites.append(CHARS)
            elif arg == ArgType.WORDCHAR:
                rule_possibilites.append(string.ascii_lowercase)
            elif arg == ArgType.COUNT:
                rule_possibilites.append([str(x) for x in range(1, max_count + 1)])
        for rule_tokens in itertools.product(*rule_possibilites):
            yield ''.join(rule_tokens)

def generate_most_rules(word_length_max=15, max_count=5):
    positions = [f'{x:X}' for x in range(word_length_max)]
    for rule in RULES:
        if rule[0] == ':':
            continue
        if len(rule) > 2:
            continue
        elif len(rule) == 2:
            if rule[1] == ArgType.POS:
                rule_possibilites = positions
            elif rule[1] == ArgType.ANYCHAR:
                rule_possibilites = CHARS
            elif rule[1] == ArgType.WORDCHAR:
                rule_possibilites = string.ascii_lowercase
            elif rule[1] == ArgType.COUNT:
                rule_possibilites = range(1, max_count + 1)
            for possibility in rule_possibilites:
                yield rule[0] + str(possibility)
        else:
            yield rule[0]

def generate_some_rules(word_length_max=15, max_count=5):
    positions = [f'{x:X}' for x in range(word_length_max)]
    for rule in RULES:
        if rule[0] == ':':
            continue
        if len(rule) > 1:
            continue
        yield rule[0]

if __name__ == "__main__":
    print(f"all: {len(list(generate_rules.generate_all_rules()))}")
    with open('all_rules.txt', 'w') as f:
        for x in generate_rules.generate_all_rules():
            f.write(x + '\n')
    print(f"most: {len(list(generate_rules.generate_most_rules()))}")
    with open('most_rules.txt', 'w') as f:
        for x in generate_rules.generate_most_rules():
            f.write(x + '\n')
    print(f"some: {len(list(generate_rules.generate_some_rules()))}")
    with open('some_rules.txt', 'w') as f:
        for x in generate_rules.generate_some_rules():
            f.write(x + '\n')
