#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import defaultdict


# find the position of a pattern in a sequence
def find_begin_position(sequence, pattern):
    for i in range(len(sequence)):
        if sequence[i] == pattern[0] and sequence[i:i+len(pattern)] == pattern:
            return i
    return -1


def parse_aligns(aligns):
    align_table = defaultdict(list)
    for align in aligns:
        s_i, t_i = align.split('-')
        align_table[int(s_i)].append(int(t_i))
    return align_table


def parse_parallel_sent(line):
    en, ch, aligns, lemmastr, tags, chunks, ch_tags = [tuple(item.split()) for item in line.strip().split(' ||| ')]
    aligns = parse_aligns(aligns)
    return en, ch, aligns, lemmastr, tags, chunks, ch_tags
