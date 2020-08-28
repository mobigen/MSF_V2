import sys, time

def DEBUG_PRINT(str_line):

    import inspect
    print("(%s,%d) %s" % (__file__, inspect.stack()[1][2], str_line.strip()))


import lib.pretreatment.textmine.morph as morph

def morph_tokenize(sent):

    return morph.get_words(sent)


mecab = None
def mecab_tokenize(sent):

    global mecab

    from konlpy.tag import Mecab
    from konlpy.utils import pprint

    if mecab == None:
        mecab = Mecab()

    word_tag_list = mecab.pos(sent)

    words = [word_tag[0] for word_tag in word_tag_list if word_tag[1][0] == 'N']

    return words


twitter = None
def twitter_tokenize(sent):

    global twitter

    from konlpy.tag import Twitter
    from konlpy.utils import pprint

    if twitter is None:
        twitter = Twitter()
    word_tag_list = twitter.pos(sent)

    words = [word_tag[0] for word_tag in word_tag_list if word_tag[1][0] == 'N']

    return words


kkma = None
def kkma_tokenize(sent):

    global kkma

    from konlpy.tag import Kkma
    from konlpy.utils import pprint

    if kkma is None:
        kkma = Kkma()
    word_tag_list = kkma.pos(sent)

    words = [word_tag[0] for word_tag in word_tag_list if word_tag[1][0] == 'N']

    return words


komoran = None
def komoran_tokenize(sent):

    global komoran
    from konlpy.tag import Komoran
    if komoran is None:
        komoran = Komoran()

    # 문장별로, 형태소 분석해서 명사, 동사만 추출해서 키워드를 리턴함
    DEBUG_PRINT("sent: %s" % (sent))

    words = komoran.pos(sent, join=True)
    words = [w for w in words if ('/NN' in w or '/XR' in w or '/VA' in w or '/VV' in w)] # 명사, 동사를 리턴함
    return words


def subword_tokenize(sent, n=3): # 형태소 분석기가 없는 경우

    def subword(token, n): # n글자짜리 부분단어를 다 추출하는 코드 
        if len(token) <= n:
            return [token]
        return [token[i:i+n] for i in range(len(token) - n)]

    # 길이 n글자인 모든 서브 스트링을 다 토큰이라고 가정하고 활용할 수도 있음
    return [sub for token in sent.split() for sub in subword(token, n)]


def simple_tokenize(sent):

    delimiters = ".,?!<>{}[]|\\/`~@#$%^&*_-=+"
    for ch in delimiters:
        sent = sent.replace(ch, " ")
    sent = sent.replace("     ", " ").replace("    ", " ").replace("   ", " ").replace("  ", " ").strip()
    return sent.split(" ")


