#!/bin/env python
# -*- coding: utf-8 -*-

import sys, re

def load_dict(_dic_path):

    n_words = {}
    j_words = {}

    fp = open(_dic_path, "r",encoding='utf-8')

    for line in fp.readlines():
        kv = line.strip().split("\t")
        for i in range(1, len(kv)):
            if kv[i][0:1] == 'n':
                n_words[kv[0]] = kv[i][0:1]
            if kv[i][0:1] == 'j':
                j_words[kv[0]] = kv[i][0:1]


    return (n_words, j_words)


def get_nouns_in(n_words, j_words, line):

    nouns = []

    for splitted in re.split('[\(\)&,”:;\- `\!\'\"\?\.]', line.strip()):

        splitted = splitted.strip()
        n = len(splitted)
        for i in range(0, n-1):
            head = splitted[0:n-i]
            tail = splitted[n-i:]


            if tail == "":
                if head in n_words.keys():
                    nouns.append(head)
            else:
                if head in n_words.keys() and tail in j_words.keys():
                    nouns.append(head)



    return nouns

dic_path = ''
n_words = None
def get_words(line):

    global n_words, j_words

    if n_words is None:
        (n_words, j_words) = load_dict(dic_path)


    return get_nouns_in(n_words, j_words, line)

