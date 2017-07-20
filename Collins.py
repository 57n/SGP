#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import defaultdict, Counter
from itertools import product

TransTable = {
    'n': 'NP',
    'adj': 'ADJP',
    'adv': 'ADVP',
    'amount': 'AMOUNT',
    'to-inf': 'to VP',
    'n.': 'NP',
    'adj.': 'ADJP'
}


# tag the duplicate NP, ADJP as NP2, ADJP2, ..., NPn, ADJPn,...
def duplicate_pattern(pat_split):
    def yield_function(pat_split):
        tagCounter = Counter()
        for token in pat_split:
            tagCounter[token] += 1
            if tagCounter[token] > 1:
                yield token + str(tagCounter[token])
            else:
                yield token
    return list(yield_function(pat_split))


def convert_pattern(pattern, transTable):
    pattern = [transTable[word] if word in transTable else word for word in pattern.split()]
    pattern = duplicate_pattern(pattern)

    # if there's '/' in the word, there are multiple candidates in the position
    pat_candidates = [word.split('/') for word in pattern]


    for tokens in product(*pat_candidates):
        yield ' '.join(tokens)


# convert patterns into a more generalized representation
def convert_patterns(headword, patterns):
    def yield_function():
        for pattern in patterns:
            for patstr in convert_pattern(pattern, transTable):
                yield patstr
    transTable = {
        'V': headword,
        'n': 'NP',
        'adj': 'ADJP',
        'adv': 'ADVP',
        'amount': 'AMOUNT',
        'to-inf': 'to VP',
        'n.': 'NP',
        'adj.': 'ADJP',
        'wh':'who/when/what/where/why/how/whether'
    }
    return set(yield_function())


def get_patterns(headword):
    return convert_patterns(headword, VerbPatterns[headword])


VerbPatterns = defaultdict(set)
for line in open('_collins.pg.v.txt'):
    word, pats = line.strip().split('\t')
    for pat in pats.replace(',',';').split(';'):
        VerbPatterns[word].add(pat.strip())

if __name__ == '__main__':
    headword = 'explain'
    patterns = get_patterns(headword)
    print(patterns)
