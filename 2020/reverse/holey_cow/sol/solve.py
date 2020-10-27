import numpy as np
from collections import defaultdict
from alphabet import *

dictionary = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
letters = [np.reshape(np.array(l), (12, 12)) for l in letters]
holes = 'ABDOPQR'

# Given a list of 0s and 1s, returns the location and length of the longest
# group of consecutive 1s, and also returns the total number of separate groups.
def num_consecutive_holes(s):
    max_len = 0
    max_idx = 0
    num_groups = 0
    l = 0
    idx = 0
    for i in range(len(s) + 1):
        if i == len(s) or not s[i]:
            if l > max_len:
                max_len = l
                max_idx = idx
                l = 0
            if i > 0 and s[i - 1]:
                num_groups += 1
        else:
            if l == 0:
                idx = i
            l += 1
    return max_len, max_idx, num_groups

def to_holes(s):
    return [1 if c in holes else 0 for c in s]

# Lookup the location in `dictionary` where a word is stored.
# Words are grouped first by the length of their consecutive group
# of ones, then by the starting index of that group, then by their
# overall length. Eeach of these properties goes a level down in the
# nested dict.
def get_location(constraint):
    length, idx, num_groups = num_consecutive_holes(constraint)
    if num_groups > 1:
        return set()
    return dictionary[length][idx][len(constraint)]

def get_word_location(word):
    return get_location(to_holes(word))

def construct_shape(phrase):
    arr = np.zeros((12, 5), dtype=int)
    for i, c in enumerate(phrase):
        padding = 4
        if i == len(phrase) - 1:
            padding = 5
        l = letters[alphabet.index(c)]
        arr = np.concatenate((arr, l, np.zeros((12, padding), dtype=int)), axis=1)
    return list(map(list, arr))

# Ensure that the line fits the following criteria with respect to space characters:
#   1. A group of consecutive 1s can be broken by at most 2 spaces, and
#   2. The sub-groups of 1s created by the spaces can not be shorter than 5 long
def check_spaces(line, constraint):
    check = False
    num_spaces = 0
    length = 0
    for i, (c, s) in enumerate(zip(line, constraint)):
        if c == 1 and check == False:
            check = True
            num_spaces = 0
        if c == 0 and check == True:
            if length <= 4 and num_spaces > 0:
                return False
            length = 0
            check = False

        if check:
            length += 1
            if s == ' ':
                if line[i - 1] == 0 or line[i + 1] == 0:
                    return False
                num_spaces += 1

        if num_spaces > 2:
            return False
    return True

# Look up a word that matches the shape of a constraint in its holeyness. 
def gen_word(constraint):
    s = get_location(constraint)
    if s and len(s) > 1:
        return s.pop()
    return None

# Recursively build a sentence by a sort of DFS. We add the longest word possible
# to the sentence that allows for satisfaction of the holeyness constraint, then recurse
# down the tree. If we get to the end of the constraint, we are done. Otherwise,
# if we can't find a word to add, recurse back up the tree and find a word that was
# 1 shorter than what we had, and try again. We also prune any branch as soon as it
# does not satisfy the constraint described above in check_spaces.
def gen_sentence(line, idx=0, words=[]):
    if not check_spaces(line[:idx - 1], ' '.join(words)):
        return None

    # Reached the bottom of the tree
    if idx == len(line) + 1:
        sentence = ' '.join(words)
        return sentence

    l = 2
    while (word := gen_word(line[idx:idx+l+2])) and idx+l < len(line):
        get_word_location(word).add(word)
        l += 1
    if l == 2:
        return None

    ret = None
    while True:
        chunk = line[idx:idx+l]
        if (word := gen_word(chunk)):
            ret = gen_sentence(line, idx+l+1, words.copy() + [word])
            if not ret and l > 0:
                get_location(chunk).add(word)
                assert word in get_location(chunk)
                l -= 1
            else:
                break
        else:
            return None

    return ret

def solve(phrase):
    lines = construct_shape(phrase)
    sentences = [gen_sentence(line) for line in lines]

    # All the words we've used so far have been taken out of the pool,
    # so now that we're done, add them back to the pool so they can be used
    # in any subsequent calls to solve()
    for line in sentences:
        for word in line.split():
            get_word_location(word).add(word)
    return '\n'.join(sentences)

count = 0
with open('dict') as f:
    for word in f.read().splitlines():
        w = word.upper()
        if len(w) < 3 or not w.encode().isalpha():
            continue
        get_word_location(w).add(w)
        count += 1

for phrase in ['ADMIN', 'FARMFORLYFE']:
    print(solve(phrase))
