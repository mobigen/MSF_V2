#!/bin/env python

def jamo_separator(ch):

    # 한글 초중종성 쪼개기

    cho = [c for c in "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"]
    jung = [c for c in "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"]
    jong = [c for c in " ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"]

    ch_code = ord(ch)

    if 0xD7A3 < ch_code or ch_code < 0xAC00:
        return ('', '', '')

    cho_idx = (ch_code - 0xAC00) // 21 // 28
    jung_idx = (ch_code - 0xAC00 - (cho_idx * 21 * 28)) // 28
    jong_idx = ch_code - 0xAC00 - (cho_idx * 21 * 28) - (jung_idx * 28)

    return (cho[cho_idx], jung[jung_idx], jong[jong_idx])


def has_ss(word):

    jong = [c for c in " ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"]
    # 단어가 쌍시옷 'ㅆ'을 가졌으면, 문장 끝일 확률이 높음.
    for ch in word:
        ch_code = ord(ch)

        if 0xD7A3 < ch_code or ch_code < 0xAC00:
            continue

        cho_idx = (ch_code - 0xAC00) // 21 // 28
        jung_idx = (ch_code - 0xAC00 - (cho_idx * 21 * 28)) // 28
        jong_idx = ch_code - 0xAC00 - (cho_idx * 21 * 28) - (jung_idx * 28)

        if (jong[jong_idx] == 'ㅆ'):
            return True

    return False


def ending_mm(last_ch):

    jong = [c for c in " ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"]

    # 감, 함, 옴 등의 'ㅁ'으로 끝나면 문장 끝일 확률이 높음
    ch_code = ord(last_ch)
    if 0xD7A3 < ch_code or ch_code < 0xAC00:
        return False

    cho_idx = (ch_code - 0xAC00) // 21 // 28
    jung_idx = (ch_code - 0xAC00 - (cho_idx * 21 * 28)) // 28
    jong_idx = ch_code - 0xAC00 - (cho_idx * 21 * 28) - (jung_idx * 28)

    if (jong[jong_idx] == 'ㅁ'):
        return True

    return False


def ending_hangul_char(last_ch):

    # 끝에 자주 나오는 글자이면 문장 끝일 확률이 높음
    # '다', '가', '까', '요', '오', '나', '뿐', '듯', '데', '함', '임', '노', '지', '냐'
    if last_ch in "다가까요오함임음냐":
        return 0.7

    if last_ch in "나뿐듯데노지":
        return 0.4

    return 0.0

def ending_char(ch):

    if ch in ".!?)>]}'#\"$`@#%^&*-_+=|\\;:./…":
        return True
    return False

def hangul_jaum(ch):

    if ch == '':
        return False

    if ch in "ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎㄲㄸㅃㅆㅉ":
        return True

    return False


def hangul_moum(ch):

    if ch == '':
        return False

    if ch in "ㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣㅘㅚㅟㅞㅙ":
        return True

    return False


def is_non_ending_exception(token_0, token_1):

    # token_0 : 앞에 어떤 경우이면, 문장 끝이 아닐까?
    # token_1 : 각종 마침 부호 및 특수문자로 끝남

    if len(token_0) == 0:
        # 특수문자 앞에 아무것도 없으면, 끝이 아닐 수 있음.
        return True

    return False


def second_ending_hangul_char(second_last_ch):

    if second_last_ch == '':
        return False

    if second_last_ch in "세네에어니":
        # print("==> second_last_ch == '%s' found." % (second_last_ch))
        return True

    return False

def is_ending(token):

    if len(token) == 0:
        return False

    # 문장 끝에 붙는 모든 종류의 특수문자 및 쓰레기들을 다 제거함.
    # 이런 것들이 뒤에 붙어 있으면, 문장 끝일 확률이 매우 높음

    # '.', '!', '?', ')', '>', ']', '\'', '\#'
    # '#', '$', '~', ...
    # 'ㅎㅎㅎ', 'ㅋㅋㅋ', '~~~', '..'
    # 끝을 의미하는 특수 문자 들임.

    n = len(token)
    end_idx = n-1

    for i in range(0, n):
        if (ending_char(token[n-i-1])):
            end_idx = n-i-1
        elif hangul_jaum(token[n-i-1]) or hangul_moum(token[n-i-1]):
            end_idx = n-i-1
        else:
            break

    # 뒤에 끝 글자 또는 그에 상응하는 글자들이 있음
    if end_idx >= 0 and ending_char(token[end_idx]) or (end_idx < n-1):
        # 문장의 끝일 가능성이 매우 높음.
        # 'ㅁ'으로 끝나면 끝일 가능성이 높음
        # '다', '요'로 끝나면 무조건 끝임

        # 여기가 끝이 아닐 가능성이 어떤 경우에 있나?
        # Jr. Mr. Ms. 이런 경우
        #
        # 여기서는 기본적으로 문장의 끝으로 보나, 예외적인 경우를 구제해 줘야 함.

        (token_0, token_1) = (token[0:end_idx], token[end_idx: ])

        # print("token_0: %s" % (token_0))
        # print("token_1: %s" % (token_1))


        if is_non_ending_exception(token_0, token_1):
            return False

        return True
    else:
        # 문장의 끝 음절로 끝나고, 앞에 'ㅆ'이 있으면 끝임.

        prob = 0.0

        last_ch = token[-1]
        second_last_ch = '';
        if len(token) > 2:
            second_last_ch = token[-2]

        prob = ending_hangul_char(last_ch)
        if prob > 0.0:
            # print("ending_hangul_char(%s) prob=%0.1f" % (token, prob))
            prob = prob

        if second_ending_hangul_char(second_last_ch):
            # print("second_ending_hangul_char(%s, %s)" % (token, second_last_ch))
            prob += 0.7

        if has_ss(token):
            # print("has_ss(%s)" % (token))
            prob += 0.5

        if ending_mm(last_ch):
            # print("has_mm(%s)" % (token))
            prob += 0.1

        if prob >= 1.0:
            # print("SEPARATOR: %s" % (token))
            return True

    # print("NON-SEPARATOR: %s" % (token))

    return False


def split_sentences(text):

    sentences = []
    cur_sequence = []

    text = text.replace("\r", " ").replace("\t", " ").replace("\n", " ").replace("   ", " ").replace("  ", " ").strip()
    tokens = text.split(" ")

    for token in tokens:
        if is_ending(token):
            cur_sequence.append(token)
            sentences.append(cur_sequence)
            cur_sequence = []
            continue
        cur_sequence.append(token)

    sentences = [" ".join(sequence) for sequence in sentences]

    return sentences


