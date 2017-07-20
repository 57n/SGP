#!/usr/bin/python
# -*- coding: utf-8 -*-


def find_continuous_chunk(chunks, condition=lambda x: x.startswith('I-')):
    for i, chunk in enumerate(chunks):
        if not condition(chunk):
            return i
    return len(chunks)


# TODO: finish aligh_tag
# TODO: deal with `-ing`
# TODO: find wh when it's tagged `WRB`
WH_TAGs = {'who', 'when', 'what', 'where','why','how','whether'}
def find_ngram_by_pattern(headword, words, lemmas, tags, chunks, patterns):
    sent_len = len(words)
    res = []

    for i, word in enumerate(words):
        
        begin = i
        if len(headword.split()) >=2:
            compound = lemmas[i-1] + " " + word
            if compound != headword:
                continue
            else:
                begin = i-1 
        elif lemmas[i] != headword or not tags[i].startswith('V'):
            continue

        pat_tag = headword.split()
    
        
        # V prep n
        if i+2 < sent_len and chunks[i+1] == 'B-PP' and chunks[i+2] == 'B-NP':
            pat = "%s %s NP" % (headword, lemmas[i+1])
            if pat in patterns:
                length = find_continuous_chunk(chunks[i+3:], lambda x: x == 'I-NP')
                ngram = tuple(tuple(headword.split()) + lemmas[i+1:i+3+length])
                ntag = tuple(pat_tag + [lemmas[i+1], 'NP'] + ['NP'] * length)
                res.append(('V %s n' % lemmas[i+1], pat, ngram, ntag, begin))
                           
        # classify V prep -ing as V prep n
        if i+2 < sent_len and chunks[i+1] == 'B-PP' and tags[i+2] == 'VBG':
            pat = "%s %s NP" % (headword, lemmas[i+1])
            if pat in patterns:
                length = find_continuous_chunk(chunks[i+3:], lambda x: x != 'O')
                ngram = tuple(tuple(headword.split()) + words[i+1:i+3+length])
                ntag = tuple(pat_tag + [lemmas[i+1], 'NP'] + ['NP'] * length)
                res.append(('V %s n' % lemmas[i+1], pat, ngram, ntag, begin))
        # V in favour of n
        if i+2 < sent_len and lemmas[i+1:i+4]==('in', 'favour', 'of') and chunks[i+4] == 'B-NP':
            pat = "%s %s NP" % (headword, 'in favour of')
            if pat in patterns:
                length = find_continuous_chunk(chunks[i+5:], lambda x: x == 'I-NP')
                ngram = tuple(tuple(headword.split()) + lemmas[i+1:i+5+length])
                ntag = tuple(pat_tag + ['in','favour','of', 'NP'] + ['NP'] * length)
                res.append(('V %s n' % 'in favour of', pat, ngram, ntag, begin))
                
        if i+2 < sent_len and lemmas[i+1:i+4]==('in', 'favour', 'of') and tags[i+4] == 'VBG':
            pat = "%s %s NP" % (headword, 'in favour of')
            if pat in patterns:
                length = find_continuous_chunk(chunks[i+5:], lambda x: x != 'O')
                ngram = tuple(tuple(headword.split()) + words[i+1:i+5+length])
                ntag = tuple(pat_tag + ['in','favour','of', 'NP'] + ['NP'] * length)
                res.append(('V %s n' % 'in favour of', pat, ngram, ntag, begin))
                
        # V prep adj
        if i+2 < sent_len and chunks[i+1] == 'B-PP' and chunks[i+2] == 'B-ADJP':
            pat = "%s %s ADJP" % (headword, lemmas[i+1])
            if pat in patterns:
                length = find_continuous_chunk(chunks[i+3:], lambda x: x == 'I-ADJP')
                ngram = tuple(tuple(headword.split()) + lemmas[i+1:i+3+length])
                ntag = tuple(pat_tag + [lemmas[i+1], 'ADJP'] + ["ADJP"] * length)
                res.append(('V %s adj' % lemmas[i+1], pat, ngram, ntag, begin))

        # V prep prep n, ex. V out of n.
        if i+3 < sent_len and chunks[i+1] == 'B-PP' and chunks[i+2] == 'B-PP' and chunks[i+3] == 'B-NP':
            pat = "%s %s %s NP" % (headword, lemmas[i+1], lemmas[i+2])
            if pat in patterns:
                length = find_continuous_chunk(chunks[i+4:], lambda x: x == 'I-NP')
                ngram = tuple(tuple(headword.split()) + lemmas[i+1:i+4+length])
                ntag = tuple(pat_tag + [lemmas[i+1],lemmas[i+2],'NP'] + ['NP'] * length)
                res.append(('V %s %s n' % (lemmas[i+1], lemmas[i+2]), pat, ngram, ntag, begin))
                
        if i+3 < sent_len and chunks[i+1] == 'B-PP' and chunks[i+2] == 'B-PP' and tags[i+3] == 'VBG':
            pat = "%s %s %s NP" % (headword, lemmas[i+1], lemmas[i+2])
            if pat in patterns:
                length = find_continuous_chunk(chunks[i+4:], lambda x: x != 'O')
                ngram = tuple(tuple(headword.split()) + words[i+1:i+4+length])
                ntag = tuple(pat_tag + [lemmas[i+1],lemmas[i+2],'NP'] + ['NP'] * length)
                res.append(('V %s %s n' % (lemmas[i+1], lemmas[i+2]), pat, ngram, ntag, begin))

        # V to-inf
        if i+2 < sent_len and chunks[i+1] == 'I-VP' and chunks[i+2] == 'I-VP':
            pat = "%s %s VP" % (headword, lemmas[i+1])
            if pat in patterns:
                length = find_continuous_chunk(chunks[i+3:], lambda x: x != 'O')
                ngram = tuple(tuple(headword.split()) + lemmas[i+1:i+3+length])
                ntag = tuple(pat_tag + [lemmas[i+1],'VP'] + ['VP'] * length)
                res.append(('V to-inf', pat, ngram, ntag, begin))
                
        # V -ing
        if i+1 < sent_len and tags[i+1] == 'VBG':
            pat = "%s -ing" % (headword)
            if pat in patterns:
                length = find_continuous_chunk(chunks[i+2:], lambda x: x != 'O')
                ngram = tuple(tuple(headword.split()) + words[i+1:i+2+length])
                ntag = tuple(pat_tag + ['VP'] + ['VP'] * length)
                res.append(('V -ing', pat, ngram, ntag, begin))
        
        # V amount
        if i+1 < sent_len and tags[i+1] == 'CD':
            pat = "%s AMOUNT" % (headword)
            if pat in patterns:
                length = find_continuous_chunk(chunks[i+2:], lambda x: x == 'I-NP')
                ngram = tuple(tuple(headword.split()) + lemmas[i+1:i+2+length])
                ntag = tuple(pat_tag + ['AMOUNT'] + ['AMOUNT'] * length)
                res.append(('V amount', pat, ngram, ntag, begin))

        # V prep amount
        if i+2 < sent_len and chunks[i+1] == 'B-PP' and tags[i+2] == 'CD':
            pat = "%s %s AMOUNT" % (headword, lemmas[i+1])
            if pat in patterns:
                length = find_continuous_chunk(chunks[i+3:], lambda x: x == 'I-NP')
                ngram = tuple(tuple(headword.split()) + lemmas[i+1:i+3+length])
                ntag = tuple(pat_tag + [lemmas[i+1],'AMOUNT'] + ['AMOUNT'] * length)
                res.append(('V %s amount' % lemmas[i+1], pat, ngram, ntag, begin))
                
        # V adj.
        if i+1 < sent_len and chunks[i+1] == 'B-ADJP': 
            pat = "%s ADJP" % (headword)
            if pat in patterns:
                length = find_continuous_chunk(chunks[i+2:], lambda x: x == 'I-ADJP')
                ngram = tuple(tuple(headword.split()) + lemmas[i+1:i+2+length])
                ntag = tuple(pat_tag + ['ADJP'] + ['ADJP'] * length)
                res.append(('V adj', pat, ngram, ntag, begin))
                pat_tag = [headword]

        # V adv.
        if i+1 < sent_len and chunks[i+1] == 'B-ADVP':
            pat = "%s ADVP" % (headword)
            if pat in patterns:
                length = find_continuous_chunk(chunks[i+2:], lambda x: x == 'I-ADVP')
                ngram = tuple(tuple(headword.split()) + lemmas[i+1:i+2+length])
                ntag = tuple(pat_tag + ['ADVP'] + ['ADVP'] * length)
                res.append(('V adv', pat, ngram, ntag, begin))
                pat_tag = [headword]

        # V that
        if i+1 < sent_len and chunks[i+1] == 'B-SBAR' and lemmas[i+1] == 'that':
            pat = "%s %s" % (headword, lemmas[i+1])
            if pat in patterns:
                length = find_continuous_chunk(chunks[i+2:], lambda x: x != 'O')
                ngram = tuple(tuple(headword.split()) + words[i+1:i+2+length])
                ntag = tuple(pat_tag + ['SBAR'] + ['SBAR'] * length)
                res.append(('V that', pat, ngram, ntag, begin))
        # V pron-refl
        if i+1 < sent_len and tags[i+1] == 'PRP' and (lemmas[i+1].endswith('self') or lemmas[i+1].endswith('selves')):
            pat = "%s pron-refl" % (headword)
            if pat in patterns:
                ngram = tuple(tuple(headword.split()) + lemmas[i+1:i+2])
                ntag = tuple(pat_tag + ['SELF'])
                res.append(('V SELF', pat, ngram, ntag, begin))
        # V wh
        if i+1 < sent_len and lemmas[i+1] in WH_TAGs:
            pat = "%s %s" % (headword, lemmas[i+1])
            if pat in patterns:
                length = find_continuous_chunk(chunks[i+2:], lambda x: x != 'O')
                ngram = tuple(tuple(headword.split()) + words[i+1:i+2+length])
                ntag = tuple(pat_tag + ['SBAR'] + ['SBAR'] * length)
                res.append(('V %s' % lemmas[i+1], pat, ngram, ntag, begin))
        # V n. ...
        if i+1 < sent_len and chunks[i+1] == 'B-NP': 
            pat_tag.append("NP")
            
            length = find_continuous_chunk(chunks[i+2:], lambda x: x == 'I-NP')
            pat_tag.extend(["NP"] * length)
            j = i + 2 + length
            # print(j, lemmas[j], chunks[j] )
            
            
            pat = "%s NP" % (lemmas[i])
            if pat in patterns:
                ngram = tuple(tuple(headword.split()) + lemmas[i+1:j])
                ntag = tuple(pat_tag)
                res.append(('V n', pat, ngram, ntag, begin))

            # V n.
            if j >= sent_len:
                pass
            # V n. prep. ...
            elif chunks[j] == 'B-PP':
                # V n. prep. n.
                if j+1 < sent_len and chunks[j+1] == 'B-NP':
                    pat = "%s NP %s NP2" % (headword, lemmas[j])
                    if pat in patterns:
                        length = find_continuous_chunk(chunks[j+2:], lambda x: x == 'I-NP')
                        ngram = tuple(tuple(headword.split()) + lemmas[i+1:j+2+length])
                        ntag = tuple(pat_tag + [lemmas[j],'NP2'] + ["NP2"] * length)
                        res.append(('V n %s n' % lemmas[j], pat, ngram, ntag, begin))
                #classify V n. prep. -ing as V n prep n
                elif j+1 < sent_len and tags[j+1] == 'VBG':
                    pat = "%s NP %s NP2" % (headword, lemmas[j])
                    if pat in patterns:
                        length = find_continuous_chunk(chunks[j+2:], lambda x: x != 'O')
                        ngram = tuple(tuple(headword.split()) + words[i+1:j+2+length])
                        ntag = tuple(pat_tag + [lemmas[j],'NP2'] + ["NP2"] * length)
                        res.append(('V n %s n' % lemmas[j], pat, ngram, ntag, begin))
                # V n. prep. adj.
                elif j+1 < sent_len and chunks[j+1] == 'B-ADJP':
                    pat = "%s NP %s ADJP" % (headword,lemmas[j])
                    if pat in patterns:
                        length = find_continuous_chunk(chunks[j+2:], lambda x: x == 'I-ADJP')
                        ngram = tuple(tuple(headword.split()) + lemmas[i+1:j+2+length])
                        ntag = tuple(pat_tag + [lemmas[j],'ADJP'] + ["ADJP"] * length)
                        res.append(('V n %s adj' % lemmas[j], pat, ngram, ntag, begin))
            # V n. VP ...
            elif chunks[j] == 'B-VP':
                # V n. to VP
                if j+1 < sent_len and chunks[j+1] == 'I-VP': 
                    pat = "%s NP %s VP" % (headword, lemmas[j])
                    if pat in patterns:
                        length = find_continuous_chunk(chunks[j+2:], lambda x: x != 'O')
                        ngram = tuple(tuple(headword.split()) + lemmas[i+1:j+2+length])
                        ntag = tuple(pat_tag + [lemmas[j],'VP'] + ['VP'] * length)
                        res.append(('V n to-inf', pat, ngram, ntag, begin))
                # V n. -ing
                if tags[j] == 'VBG':
                    pat = "%s NP -ing" % (headword)
                    if pat in patterns:
                        length = find_continuous_chunk(chunks[j+1:], lambda x: x != 'O')
                        ngram = tuple(tuple(headword.split()) + words[i+1:j+1+length])
                        ntag = tuple(pat_tag + ['VP'] + ['VP'] * length)
                        res.append(('V n -ing', pat, ngram, ntag, begin))
            # V n. n.
            elif chunks[j] == 'B-NP': 
                pat = "%s NP NP2" % (headword)
                if pat in patterns:
                    length = find_continuous_chunk(chunks[j+1:], lambda x: x != 'O')
                    ngram = tuple(tuple(headword.split()) + lemmas[i+1:j+1+length])
                    ntag = tuple(pat_tag + ['NP2'] + ['NP2'] * length)
                    res.append(('V n n', pat, ngram, ntag, begin))

#             # V n.
#             else:
#                 pat = "%s NP" % (lemmas[i])
#                 if pat in patterns:
#                     ngram = lemmas[i:j]
#                     res.append([pat, ngram, align_tag])
#                 break

    return res


if __name__ == '__main__':
    from utils import get_sent_info
    from Collins import get_patterns

    headword = 'run'
    patterns = get_patterns(headword)
    corpus = [get_sent_info(line) for line in open("verbs/{0}.txt".format(headword))]

    for en, ch, aligns, lemmas, tags, chunks, ch_tags in corpus:
        enPatNgrams = find_ngram_by_pattern(headword, en, lemmas, tags, chunks, patterns)
        if enPatNgrams:
            for en_pat, ngram, ntag in enPatNgrams:
                print('{}: {} ({})'.format(en_pat, ' '.join(ngram), ' '.join(ntag)))
