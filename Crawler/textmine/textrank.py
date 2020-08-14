
from collections import Counter

def scan_vocabulary(sents, tokenize, min_count=2):

    counter = Counter(w for sent in sents for w in tokenize(sent))
    counter = {w:c for w,c in counter.items() if c >= min_count}

    idx_to_vocab = [w for w, _ in sorted(counter.items(), key=lambda x:-x[1])]
    vocab_to_idx = {vocab:idx for idx, vocab in enumerate(idx_to_vocab)}
    return idx_to_vocab, vocab_to_idx


from collections import defaultdict

def cooccurrence(tokens, vocab_to_idx, window=2, min_cooccurrence=2):

    counter = defaultdict(int)
    for s, tokens_i in enumerate(tokens):
        vocabs = [vocab_to_idx[w] for w in tokens_i if w in vocab_to_idx]
        n = len(vocabs)
        for i, v in enumerate(vocabs):
            if window <= 0:
                b, e = 0, n
            else:
                b = max(0, i - window)
                e = min(i + window, n)
            for j in range(b, e):
                if i == j:
                    continue
                counter[(v, vocabs[j])] += 1
                counter[(vocabs[j], v)] += 1
    counter = {k:v for k,v in counter.items() if v >= min_cooccurrence}
    n_vocabs = len(vocab_to_idx)
    return dict_to_mat(counter, n_vocabs, n_vocabs)

from scipy.sparse import csr_matrix

def dict_to_mat(d, n_rows, n_cols):

    rows, cols, data = [], [], []
    for (i, j), v in d.items():
        rows.append(i)
        cols.append(j)
        data.append(v)
    return csr_matrix((data, (rows, cols)), shape=(n_rows, n_cols))

def word_graph(sents, tokenize=None, min_count=2, window=2, min_cooccurrence=2):

    idx_to_vocab, vocab_to_idx = scan_vocabulary(sents, tokenize, min_count)
    tokens = [tokenize(sent) for sent in sents]
    g = cooccurrence(tokens, vocab_to_idx, window, min_cooccurrence)
    return g, idx_to_vocab




import numpy as np


def pagerank(x, df=0.85, max_iter=30):
    from sklearn.preprocessing import normalize
    assert 0 < df < 1

    # initialize
    A = normalize(x, axis=0, norm='l1')
    R = np.ones(A.shape[0]).reshape(-1,1)
    bias = (1 - df) * np.ones(A.shape[0]).reshape(-1,1)

    # iteration
    for _ in range(max_iter):
        R = df * (A * R) + bias

    return R


def simple_tokenize(sent):

    delimiters = ".,?!<>{}[]|\\/`~@#$%^&*_-=+"
    for ch in delimiters:
        sent = sent.replace(ch, " ")
    sent = sent.replace("     ", " ").replace("    ", " ").replace("   ", " ").replace("  ", " ").strip()
    return sent.split(" ")


def textrank_sent_sim(s1, s2):

    n1 = len(s1)
    n2 = len(s2)
    if (n1 <= 1) or (n2 <= 1):
        return 0
    common = len(set(s1).intersection(set(s2)))
    base = math.log(n1) + math.log(n2)
    return common / base


def cosine_sent_sim(s1, s2):

    if (not s1) or (not s2):
        return 0

    s1 = Counter(s1)
    s2 = Counter(s2)
    norm1 = math.sqrt(sum(v ** 2 for v in s1.values()))
    norm2 = math.sqrt(sum(v ** 2 for v in s2.values()))
    prod = 0
    for k, v in s1.items():
        prod += v * s2.get(k, 0)
    return prod / (norm1 * norm2)


def textrank_keywords(sents, tokenize=simple_tokenize, min_count=2, window=5, min_cooccurrence=2, df=0.85, max_iter=30, topk=30):

    g, idx_to_vocab = word_graph(sents, tokenize, min_count, window, min_cooccurrence)

    # 예외처리
    if len(idx_to_vocab) == 0: return []

    R = pagerank(g, df, max_iter).reshape(-1)
    idxs = R.argsort()[-topk:]
    keywords = [(idx_to_vocab[idx], R[idx]) for idx in reversed(idxs)]
    return keywords



from collections import Counter
from scipy.sparse import csr_matrix
import math

def sent_graph(sents, tokenize, similarity=textrank_sent_sim, min_count=2, min_sim=0.3):

    _, vocab_to_idx = scan_vocabulary(sents, tokenize, min_count)
    
    tokens = [[w for w in tokenize(sent) if w in vocab_to_idx] for sent in sents]
    rows, cols, data = [], [], []
    n_sents = len(tokens)

    for i, tokens_i in enumerate(tokens):
        for j, tokens_j in enumerate(tokens):
            if i >= j:
                continue
            sim = similarity(tokens_i, tokens_j)
            if sim < min_sim:
                continue
            rows.append(i)
            cols.append(j)
            data.append(sim)
    return csr_matrix((data, (rows, cols)), shape=(n_sents, n_sents))


def textrank_keysentences(sents, tokenize=simple_tokenize, min_count=2, similarity=textrank_sent_sim, df=0.85, max_iter=30, topk=5, min_sim=0.3):

    # 예외처리
    if len(sents) == 0: return []
    if len(sents) == 1: return [[0, 0.0, sents[0]]]

    g = sent_graph(sents, tokenize=tokenize, similarity=similarity, min_count=min_count, min_sim=min_sim)
    R = pagerank(g, df, max_iter).reshape(-1)
    idxs = R.argsort()[-topk:]
    keysents = [(idx, R[idx], sents[idx]) for idx in reversed(idxs)]
    return keysents


