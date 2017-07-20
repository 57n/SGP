
# coding: utf-8

# In[495]:

from collections import Counter, defaultdict
import sys

# In[542]:

VerbTags = ['VA', 'VAC', 'VB', 'VC', 'VCL', 'VD', 'VE', 'VF', 'VG', 'VH', 'VHC', 'VI', 'VJ', 'VK', 'VL', 'V_2']
NounTags = ['Na', 'Nb', 'Nc', 'Ncd', 'Nd', 'Neu', 'Nes', 'Nep', 'Neqa', 'Neqb', 'Nf', 'Ng', 'Nh', 'Nv']
ConjTags = ['Caa', 'Cab', 'Cba', 'Cbb']
AdvTags = ['Da', 'Dfa', 'Dfb', 'Di' , 'Dk', 'D']

tagAbbrDict = {pos: pos[0] for pos in VerbTags + NounTags + ConjTags + AdvTags}

function_words = {'了', '，', ",", '、'}
punctuation = {'？','，',',','、','。','?', '﹐'}
pattern_elements = {'S', 'NP', 'NP2', 'VP', 'ADJP', 'ADVP', 'AMOUNT', 'SBAR', 'SELF'}


# ### Find ngram example for patterns from sentence

# In[543]:

from find_pattern_ngram import find_ngram_by_pattern


# In[544]:

from itertools import groupby

def ntag2pat(ntag, en_pat):
    ntag = [tag for tag in ntag if tag != '_']
    pat = [(tag, len(list(tags))) for tag, tags in groupby(ntag)]
    tag_count = defaultdict(int)
    
    if en_pat.split()[-1] in {'who', 'when', 'what', 'where', 'why', 'how', 'whether'}:
        return [item[0] for item in pat]
    else:
        for tag, count in pat:
            tag_count[tag] = max(tag_count[tag], count)
        res = []
        for tag, count in reversed(pat): #if multiple tag are in the same count, assign tag to the latter location because 
            if count >= tag_count[tag] and tag not in res: #the tags are not usually appearing in the first location in chinese
                res.insert(0, tag)
    return res


# ### Generate SPG

# Generate SPG from EN pattern, ngram, en_pos, and corresponding ch_ngram, ch_pos

# In[546]:

# Conver CH_PATTERN into template (e.g., '描述 NP' -> 'V NP')
def to_template(pat, tags):
    tags = [tag if tag not in tagAbbrDict else tagAbbrDict[tag] for tag in tags]
    i = 0
    res = []
    for token in pat.split():
        if token in pattern_elements:
            res.append(token)
        else:
            res.append(tags[i])
            i += 1
    
    return ' '.join(res)


# In[547]:

#from utils import find_begin_position

def find_tag_by_pat(en_pat):
    trans = {'who':'SBAR', 'when':'SBAR', 'what':'SBAR', 'where':'SBAR', 'why':'SBAR', 'how':'SBAR', 'whether':'SBAR' , 'that':'SBAR', 'pron-refl':'SELF' , '-ing':'VP'}
    en_pat_set = set([word if word not in trans else trans[word] for word in en_pat.split()])
    return en_pat_set & pattern_elements
    
def genSPG(ch, eng, lemmas, begin_index, ngram, aligns, en_pat, align_tag, ch_tags):
    
    #begin_index = find_begin_position(eng, lemmas, ngram)
    #print(begin, begin_index)
    if begin_index >= 0:
        # get the pattern word index
        en_indice = list(range(begin_index, begin_index+len(ngram)))
        ch_indice = [j for i in en_indice for j in aligns[i]]
#         print(en_indice)
#         print(ch_indice)
        en_pat_indice = [i for i in en_indice if lemmas[i] in en_pat.split() or eng[i] in en_pat.split()]
        ch_pat_indice = [j for i in en_pat_indice for j in aligns[i]]
#         print(en_pat_indice)
#         print(ch_pat_indice)
        
        if not ch_pat_indice:
            return

        ch_begin_index = min(ch_indice)
        ch_end_index = max(ch_indice) + 1
#         print(ch_begin_index, ch_end_index)

        cpat = [ch[i] if i in ch_pat_indice and ch[i] not in function_words else '_' for i in range(ch_begin_index, ch_end_index)]
        cpat_tag = [tag for i, tag in enumerate(ch_tags[ch_begin_index:ch_end_index]) if cpat[i] != '_']
#         print(cpat, cpat_tag,  align_tag)
        # Insert tag by align_tag
        for i, en_index in enumerate(en_indice):
            for ch_index in aligns[en_index]:
                if ch_index not in ch_pat_indice:
                    cpat[ch_index - ch_begin_index] = align_tag[i]
        cpat = ntag2pat(cpat, en_pat)
        
        # check
        phrase_tag_in_eng = find_tag_by_pat(en_pat)
        phrase_tag_in_cpat = set(cpat) & pattern_elements
        #if phrase_tag == phrase_tag_in_cpat, it means all phrase tag appearing in the cpat exactly once.
        if phrase_tag_in_eng != phrase_tag_in_cpat or set(cpat) == phrase_tag_in_eng:
            cpat = None
        
    else:
        print("can't not find: ",eng,ngram)
        cpat = None
        
    if cpat and cpat_tag:
        cpat = ' '.join(cpat)
        template = to_template(cpat, cpat_tag)
        ch_ngram = ch[ch_begin_index:ch_end_index]
        # ch_pat, ch_pat_tag, en_ngram, ch_ngram
        return cpat, template, ' '.join(ngram), ' '.join(ch_ngram)


# ### Filter out less frequent patterns

# In[672]:

from math import sqrt, ceil
from numpy import mean, var

def compute_threshold(sequence):
    avg = mean(sequence)
    std = sqrt(var(sequence))
    # threshold = average + 0.5 * standard_deviation
    return avg + 0.5 * std

def weighted_score(en_group, template, freq):
    weight_table = {}
    if en_group == 'V from n':
        weight_table = {'V NP':1.03 ,'V P NP':13, 'P NP V':4 , 'P NP':0.2 , 'NP N':0.5, 'N NP':0.8}
    elif en_group == 'V toward n':
        weight_table = {'V NP':1.03 ,'P NP V':5, 'P NP':0.3 , 'NP N':0.5, 'N NP':0.8}
    elif en_group == 'V like n':
        weight_table = {'D D V NP':9, 'D SHI NP':15 , 'D V NP':1.3 ,'D V SHI NP':10, 'V DE V NP':10 ,'V P NP':5 ,'V D NP':3 ,'NP V':0.4 ,'N NP':0.1 , 'P NP':0.1 , 'V NP V V':5}
    elif en_group == 'V n against n':
        weight_table = {'V NP':1.03 ,'V NP V NP2':1.5, 'V NP D NP2':3 , 'V NP D V NP2':5 , 'P NP V NP2':4 , 'V NP D P NP2':3.75}
    elif en_group == 'V for n':
        weight_table = {'V NP':1.03 ,'P NP V':12, 'P NP':0.25 , 'D NP':0.5 , 'NP N':0.5 , 'N NP':0.8}
    elif en_group == 'V n with n':
        weight_table = {'C NP2 V NP':2.5 , 'P NP2 V NP':1.5}
    elif en_group == 'V out of n':
        weight_table = {'V NP':1.03 ,'P NP':0.5, 'D NP':0.3 , 'DE NP': 0.8 , 'NP N':0.5, 'N NP':0.8}
    elif en_group == 'V adj':
        weight_table = {'V ADJP':2.5, 'ADJP SHI':0.4 , 'DE ADJP':0.3 , 'ADJP DE':0.6 , 'P ADJP':0.18 , 'ADJP P':0.5}
    elif en_group == 'V at n':
        weight_table = {'V NP':1.03 ,'P NP':0.25, 'D NP':0.7 , 'P NP V':20 , 'NP N':0.5, 'N NP':0.8 , 'V P NP':4.6}
    elif en_group == 'V after n':
        weight_table = {'V NP':1.03 ,'D NP':0.6, 'N NP':0.8 , 'NP N':0.5}
    elif en_group == 'V n':
        weight_table = {'V NP':1.03 ,'D NP':0.15, 'SHI NP':0.15 , 'P NP':0.2 , 'P NP V':9 , 'V NP V':5, 'NP D':0.4 , 'NP N':0.2 , 'NP V':0.4, 'N NP':0.8}
    elif en_group == 'V to n':
        weight_table = {'V NP':1.03 ,'P NP':0.15 , 'D NP':0.15, 'N NP':0.8, 'NP N':0.5 , 'P NP V':2}
    elif en_group == 'V in n':
        weight_table = {'V NP':1.03 ,'P NP':0.2, 'D NP':0.5 , 'NP N':0.5, 'N NP':0.8 , 'P NP N V':7}
    elif en_group == 'V around n':
        weight_table = {'V NP':1.03 ,'P NP N V':54, 'V D NP V':14 , 'V D NP':1.5 , 'D NP V':54 , 'P NP V':9 , 'NP N':0.5, 'N NP':0.8}
    elif en_group == 'V n to-inf':
        weight_table = {'V NP D VP':4.5}
    elif en_group == 'V to-inf':
        weight_table = {'VP D':0.5 , 'DE VP':0.5 , 'P VP':0.5}
    elif en_group == 'V on n':
        weight_table = {'V NP':1.03 ,'P NP':0.15, 'D NP':0.3 , 'DE NP':0.5 , 'P NP V':10 , 'NP N':0.5, 'N NP':0.8 , 'V P NP N':6 ,'P NP N V':8}
    elif en_group == 'V towards n':
        weight_table = {'V NP':1.03 ,'P NP V':5 , 'P NP':0.3 ,'D NP':0.3, 'NP N':0.5, 'N NP':0.8}
    elif en_group == 'V with n':
        weight_table = {'V NP':1.03 ,'P NP V':4, 'P NP D V':6, 'C NP V':8 , 'C NP':0.3 , 'D NP':0.4 ,'P NP N':0.8 ,'DE NP':0.5 ,'V NP V':4 , 'NP N':0.7, 'N NP':0.8}
    elif en_group == 'V as n':
        weight_table = {'V NP':1.03 ,'V V NP':3, 'V NP V':3 , 'P NP':0.5 , 'D NP':0.5, 'V P NP':3, 'NP N':0.5, 'N NP':0.8}
    elif en_group == 'V n about n':
        weight_table = {'V NP V NP2':4, 'P NP V NP2':2 , 'V NP P NP2':4 , 'V NP D NP2':11 , 'V NP N NP2':3.5, 'P NP V D NP2':7}
    elif en_group == 'V n as n':
        weight_table = {'P NP V NP2':2, 'V NP V NP2':2 , 'P NP P NP2':9 ,'V NP P NP2':8 , 'P NP V V NP2':20 , 'P NP V P NP2':50 ,'P NP D NP2':50 , 'NP V NP2':0.3}
    elif en_group == 'V before n':
        weight_table = {'V NP':1.03 ,'P NP N V':9, 'NP N':0.5, 'N NP':0.8}
    elif en_group == 'V into n':
        weight_table = {'V NP':1.03 ,'D NP':0.5, 'P NP':0.5 , 'NP V':0.45, 'NP N':0.5, 'N NP':0.8}
    elif en_group == 'V about n':
        weight_table = {'V NP':1.03 ,'P NP V':10, 'NP N':0.5, 'N NP':0.8 , 'V P NP':4.5}
    elif en_group == 'V over n':
        weight_table = {'V NP':1.03 ,'P NP V':10, 'NP N':0.5, 'N NP':0.8}
    elif en_group == 'V n n':
        weight_table = {'P NP V NP2':10 , 'P NP2 V NP':10 , 'NP V NP2':0.3 , 'NP2 V NP':0.4 , 'V NP V NP2':2 , 'V NP2 V NP':2}
    elif en_group == 'V against n':
        weight_table = {'V NP':1.03 ,'NP N':0.5, 'N NP':0.8}
    if template in weight_table:
        degree = weight_table[template]
    else:
        degree = 1
    return ceil(freq * degree)

def read_valid_template():
    valid = {}
    # the valid chinese template is >= avg + std
    for line in open('en_pat.ch_pat.txt'):
        line = line.strip().split('\t')
        en_group = line[0]
        valid[en_group] = set(line[1:])
    return valid

def SPG_filter(en_group,SPGs):
    
    (_,_),max_freq = SPGs[0]
    freq_seq = [ freq for (ch_pat, template), freq in SPGs]
    threshold = compute_threshold(freq_seq)
    
    filtered_SPGs = Counter()
    for (ch_pat, template), freq in SPGs:
        if en_group in VALID_TEMPLATE:
            if template in VALID_TEMPLATE[en_group] or freq >= threshold:
                filtered_SPGs[(ch_pat, template)] += weighted_score(en_group, template, freq)
        else:
            if freq >= threshold:
                filtered_SPGs[(ch_pat, template)] += weighted_score(en_group, template, freq)
                                                                    
    return filtered_SPGs


def example_score(examples, en_pat, ch_pat):
    eng = examples[0]
    ch = examples[1]
    first_word_in_chpat = ch_pat.split()[0]
    Q = len(en_pat.split())

    # I think most phrase tag is in two word, and SBAR contain 5 word
    for tag in find_tag_by_pat(en_pat): 
        if tag == 'SBAR':
            Q += 5
        else:
            Q += 2

    if first_word_in_chpat in pattern_elements:
        R = 1
    else:
        # the first word in sentence must be the same with the chinese pattern, or it will get a penalty.
        if ch.split()[0] == first_word_in_chpat: 
            R =1
        else:
            R = 5

    if any(word in punctuation for word in ch.split()):
        R = 3


    score = ( 2 * (abs(len(eng.split())/1.28 - len(ch.split()))+1) + ( abs(Q - len(eng.split())) + 1 ) ) * R
    return score

# In[668]:

from Collins import get_patterns, convert_patterns
from utils import parse_parallel_sent

VALID_TEMPLATE = read_valid_template()
# ### Generate SPG from Corpus
headword = sys.argv[1]


try:
    patterns = convert_patterns(headword, [sys.argv[2]])
except:
    patterns = get_patterns(headword)

# ### Load parallel corpus to generate SPG
try:
    corpus = [parse_parallel_sent(line) for line in open("Verbs/{0}.txt".format(headword))]
except:
    corpus = [parse_parallel_sent(line) for line in open("MIXED-Corpus.all") if headword in line]
# initialize pattern counter and pattern example dictionary
# Counter for chinese patterns: EN_PATTERN -> CH_PATTERN -> count
chPatCount = defaultdict(Counter)
# pattern example dictionary: EN_PATTERN -> CH_PATTERN -> Example parallel ngrams (en, ch)
patExamples = defaultdict(lambda: defaultdict(list))

# Generate SPG from corpus
for en, ch, aligns, lemmas, tags, chunks, ch_tags in corpus:
    enPatNgrams = find_ngram_by_pattern(headword, en, lemmas, tags, chunks, patterns)
    if enPatNgrams:
        for en_group, en_pat, ngram, align_tag, begin in enPatNgrams:
            res = genSPG(ch, en, lemmas, begin, ngram, aligns, en_pat, align_tag, ch_tags)
            if res:
                ch_pat, ch_pat_tag, en_ngram, ch_ngram = res
                if en_ngram not in [eng for eng,ch in patExamples[en_pat][ch_pat]]:
                    patExamples[en_pat][ch_pat].append((en_ngram, ch_ngram))
                chPatCount[(en_group, en_pat)][(ch_pat, ch_pat_tag)] += 1

print(headword)
for (en_group, en_pat), ch_pat_counter in chPatCount.items():
    ch_pats = ch_pat_counter.most_common()
    valid_spg_counter = SPG_filter(en_group, ch_pats)
    print(en_pat)
    for (cpg, ch_template), score in valid_spg_counter.most_common(10):
        good_examples = sorted(patExamples[en_pat][cpg],key = lambda x: example_score(x, en_pat , cpg))
        freq = len(good_examples)
        print(' ', cpg, '\t' + str(freq))
        try:
            times = int(sys.argv[3])
            for eng ,ch in good_examples[:times]:
                print('\t\t',eng, ch.replace(" ",''))
        except:
            pass
    print()
        

