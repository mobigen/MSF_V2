//-----------------------------------------------------------------------------
// StrUtil.cpp --
//   C++ String 핸들링 클래스
//
// Authors: Mobigen Co., Ltd. (c) All rights Reserved.
//
// Updates:
//   2004/06/11 ca2sp() 추가됨
//   2004/05/21 replaceFirst() 추가됨
//   2004/05/04 strstrIgnoreCase() added. 대소문자 구분하지 않는 strstr()임.
//
//   2004/03/03 libWeb/StrList에서 split()함수를 복사해 옴. split()개념을
//              이렇게 잡음.
//            * "a|b|c|"를 "|"로 자르면 ("a", "b", "c")가 나옴.
//            * "|a||b|c||"를 "|"로 자르면 ("", "a", "", "b", "c", "")가 나옴.
//            주의: Perl에서는 맨끝에 오는 Delimiter들은 모두 무시함.
//
//   2003/03/04 존재하는 모든 복사 연산을 제거함.
//   2003/01/22 replace(str, x, y) added
//-----------------------------------------------------------------------------

#include "StrUtil.h"

#include <stdio.h>
#include <unistd.h> // atoi()
#include <string.h> // memcpy()
#include <assert.h> // assert()
#include <ctype.h>  // tolower(), toupper()

#include <string>

#include <algorithm>
#include <cctype>
#include <fstream>
#include <iostream>

using namespace std;

#ifndef DEBUG_PRINT
#  ifdef NDEBUG
#    define DEBUG_PRINT if (0) printf
#  else
#    define DEBUG_PRINT printf("(%s,%d) ", __FILE__, __LINE__); printf
#  endif // NDEBUG
#endif // DEBUG_PRINT

string StrUtil::trim_undesirable(const string &s1, const string &u1)
{
    // char str[s1.size()+1]; // FIXME: stack overflow의 원인임.

    char *str = (char*) malloc(s1.size()+1);
    strcpy(str, s1.c_str());
    const char *undesirable = u1.c_str();

    int i, j;
    char *result;
    assert(str != NULL);
    assert(undesirable != NULL);

    result = str;
    j = 0;
    for (i = 0; str[i] != '\0'; i++) {
        if (strchr(undesirable, str[i]) == NULL) {
            result[j] = str[i]; j++;
        }
    }

    result[j] = '\0';

    string a = str;
    free(str);

    return a;
}

string StrUtil::replaceFirst(const string &str,
          const string &a, const string &b)
{
    // str 에서 처음 나오는 a 를 찾아서 b 로 바꾼 스트링을 리턴
    string str2 = str;

    int position = str.find(a);

    if (position == (int) string::npos) { // a가 없으면 원문 그대로 리턴
        return str2;
    }

     return str2.replace(position, a.length(), b);
}

string StrUtil::replace(const string &str, const string &x, const string &y)
{
    string result = "";

    int from = 0, to = 0;

    char *str_c_str = (char*) str.c_str();
    char *x_c_str = (char*) x.c_str();
    int x_size = x.size();

    for (int i = 0, n = str.size(); i < n; i++) {
        if (strncmp(&str_c_str[i], x_c_str, x_size) == 0) {
            result += str.substr(from, to-from);
            result += y;

            from = i + x_size;
            to = from;

            i += x_size - 1;
        } else {
            to++;
            // result += str.substr(i, 1);
        }
    }

    if (to > from) {
        result += str.substr(from, to-from);
    }

    return result;
}

string StrUtil::tolower(const string &str)
{
    string tmp = str;

    for (int i = 0, n = tmp.size(); i < n; i++) {
        *((char*)(&tmp[i])) = ::tolower(tmp[i]);
    }

  #if 0
    for (int i = 0, n = str.size(); i < n; i++) {
        char *p = (char*) &(str.c_str()[i]);
        *p = ::tolower(*p);
    }
  #endif

  #if 0
    transform(tmp.begin(), tmp.end(), tmp.begin(), (int(*)(int)) ::tolower);
  #endif

    return tmp;
}

string StrUtil::toupper(const string &str)
{
    string tmp = str;

    for (int i = 0, n = tmp.size(); i < n; i++) {
        *((char*)(&tmp[i])) = ::toupper(tmp[i]);
    }

  #if 0
    transform(tmp.begin(), tmp.end(), tmp.begin(), (int(*)(int)) ::toupper);
  #endif

    return tmp;
}

/*
bool StrUtil::equalsIgnoreCase(const string &str1, const string &str2)
{
    string str_1 = StrUtil::toupper(str1);
    string str_2 = StrUtil::toupper(str2);

    return (str_1 == str_2);
}
*/

int StrUtil::findIgnoreCase(const string &str, const string &x)
{
    string tmp_str = StrUtil::tolower(str);
    string tmp_x = StrUtil::tolower(x); 

    int pos = tmp_str.find(tmp_x, 0);

    return pos;
}

// static
string StrUtil::trim(const string &str)
{
    int i = str.size()-1;
    char *str_c_str = (char*) str.c_str();

    // 뒤에서 앞으로 오면서, 공백이 아닌 첫번째 글자 찾기
    for (  ; i >= 0; i--) {
        char c = str_c_str[i];
        if (c == ' ' || c == '\t' || c == '\r' || c == '\n') {
            continue;
        } else {
            break;
        }
    }

    return str.substr(0, i+1);
}

// static
string StrUtil::trim_blanks(const string &str) 
{
    // 2002/02/14 버퍼를 새로 할당함으로써,
    //            원문이 Overwrite 되는 현상을 제거함.

    // "  xx y z \t " --> "xx y z"

    // char str2[str.size()+1]; // FIXME: stack overflow를 만드는 범인임.

    char *str2; str2 = (char*) malloc(str.size()+1);
    // string str2(str);
    // strcpy(str2, str.c_str()); // 굳이 미리 복사할 필요도 없음.

    int j = 0;
    bool prev_blank = true;
    char *str_c_str = (char*) str.c_str();
    // char *str2_c_str = (char*) str2.c_str();
    char *str2_c_str = (char*) str2;

    assert(str_c_str != str2_c_str);

    for (int i = 0, n = str.size(); i < n; i++) {
        if (str_c_str[i] == ' ' || str_c_str[i] == '\t' ||
            str_c_str[i] == '\n' || str_c_str[i] == '\r')
        {
            if (prev_blank) {
                // skip
            } else {
                str2_c_str[j] = ' ';
                prev_blank = true;
                j++;
            }
        } else {
            str2_c_str[j] = str_c_str[i];
            j++;
            prev_blank = false;
        }
    }

    if (j > 0 && prev_blank) {
        j--;
    }
    str2_c_str[j] = '\0';

    // return str2.substr(0, j);
    string a = str2; // string(str2);

    free(str2);

    return a;
}

string StrUtil::ca2sp(const string &str)
{
     /// "aaa^Abb^Bc" --> "aaa bb c"
     // string str2 = str;
     char *str2 = (char*) malloc(str.size() + 1);

     int j = 0;
     char *str_c_str = (char*) str.c_str();
     char *str2_c_str = (char*) str2;

     assert(str_c_str != str2_c_str);

     for (int i = 0, n = str.size(); i < n; i++) {
         int str_c_ascii = int(str_c_str[i]);
         if ((0 <= str_c_ascii && str_c_ascii <= 31) || str_c_ascii == 127) {
                 str2_c_str[j] = ' ';
                 j++;
         } else {
             str2_c_str[j] = str_c_str[i];
             j++;
         }
     }

     str2_c_str[j] = '\0';

     return str2;
}

// static 
string StrUtil::trim_crlf(const string &str)
{
    int i = str.size()-1;
    char *str_c_str = (char*) str.c_str();

    // 뒤에서 앞으로 오면서, 공백이 아닌 첫번째 글자 찾기
    for (  ; i >= 0; i--) {
        char c = *(str_c_str+i);
        if (c == '\r' || c == '\n') {
            continue;
        } else {
            break;
        }
    }

    return str.substr(0, i+1);
}

// static
int StrUtil::string2int(const string &str)
{
    return atoi(str.c_str());
}

string StrUtil::int2string(int i)
{
    char buf[32]; sprintf(buf, "%d", i);
    return string(buf);
}



// static
float StrUtil::string2float(const string &str)
{
    float f = 0.0;

    sscanf(str.c_str(), "%f", &f);

    return f;
}

string StrUtil::float2string(float f, int r /* default 2 */)
{
    char format[10]; sprintf(format, "%%.%df", r);
    char buf[32]; sprintf(buf, format, f);

    return string(buf);
}

long StrUtil::string2long(const string &str)
{
    return atol(str.c_str());
}

string StrUtil::long2string(long i)
{
    char buf[32]; sprintf(buf, "%ld", i);
    return string(buf);
}


string StrUtil::join(const string &glue, vector<string> &tokens)
{
    int glue_size = glue.size();
    char *glue_c_str = (char*) glue.c_str();

    int total_len = 0;

    for (int i = 0, n = tokens.size(); i < n; i++) {
        total_len += tokens[i].size(); 
    }

    if (tokens.size() > 0) {
        total_len += (glue_size * (tokens.size() - 1));
    }

    assert(total_len >= 0);

    string result;
                              // stack overflow?
    result.resize(total_len); // FIXME: pre allocation of buffer

    char *result_c_str = (char*) result.c_str();

    int pos = 0;
    for (int i = 0, n_tokens = tokens.size(); i < n_tokens; i++) {
        strncpy(&result_c_str[pos], 
                tokens[i].c_str(), tokens[i].size());
        pos += tokens[i].size();

        result_c_str[pos] = '\0';

        if (i < n_tokens-1) {
            strncpy(&result_c_str[pos],
                   glue_c_str, glue_size);
            pos += glue_size;
            result_c_str[pos] = '\0';
        }
    }

    return result;
}

string StrUtil::join_deque(const string &glue, deque<string> &tokens)
{
    int glue_size = glue.size();
    char *glue_c_str = (char*) glue.c_str();

    int total_len = 0;

    for (int i = 0, n = tokens.size(); i < n; i++) {
        total_len += tokens[i].size(); 
    }

    if (tokens.size() > 0) {
        total_len += (glue_size * (tokens.size() - 1));
    }

    assert(total_len >= 0);

//  string result("", total_len);
    string result;
                              // stack overflow?
    result.resize(total_len); // FIXME: pre allocation of buffer

    char *result_c_str = (char*) result.c_str();

    int pos = 0;
    for (int i = 0, n_tokens = tokens.size(); i < n_tokens; i++) {
        strncpy(&result_c_str[pos], 
                tokens[i].c_str(), tokens[i].size());
        pos += tokens[i].size();

        result_c_str[pos] = '\0';

        if (i < n_tokens-1) {
            strncpy(&result_c_str[pos],
                   glue_c_str, glue_size);
            pos += glue_size;
            result_c_str[pos] = '\0';
        }
    }

    return result;
}

vector<string> StrUtil::split(const string &str, const string &delim,
       int num) // default = 0
{
    vector<string> tokens;

    StrUtil::split(str, tokens, delim, num);

    return tokens;
}

deque<string> StrUtil::split_deque(const string &str, const string &delim,
       int num) // default = 0
{
    deque<string> tokens;

    StrUtil::split_deque(str, tokens, delim, num);

    return tokens;
}

void StrUtil::split(const string& str,
         vector<string>& tokens,
         const string& delimiters, // default = " "
         int num)                  // default = 0
{
#if 1
  {
    char *p0 = (char*) str.c_str();
    char *p = (char*) str.c_str();
    char *delimiter = (char*) delimiters.c_str();
    char *q = NULL;

    int count = 0;
    while ((q = strstr(p, delimiter)) != NULL) {
        const string &token = str.substr(p-p0, q-p);
        if (num > 0 && ++count >= num) {
            break;
        }
        tokens.push_back(token);
        p = q + delimiters.size();
    }

    if (*p != '\0') {
        const string &token = str.substr(p-p0);
        tokens.push_back(token);
    }
  }
#endif

#if 0
    // Skip delimiters at beginning.
    string::size_type lastPos = str.find_first_not_of(delimiters, 0);

    // Find first "non-delimiter".
    string::size_type pos = str.find_first_of(delimiters, lastPos);

    int count = 0;
    while (string::npos != pos || string::npos != lastPos) {
        count++;
        if (num != 0 && count >= num) {
            tokens.push_back(str.substr(lastPos, str.size()-lastPos));
            break;
        }

        // Found a token, add it to the vector.
        tokens.push_back(str.substr(lastPos, pos - lastPos));

        // Skip delimiters.  Note the "not_of"
        lastPos = str.find_first_not_of(delimiters, pos);
        // Find next "non-delimiter"
        pos = str.find_first_of(delimiters, lastPos);
    }
#endif
}

void StrUtil::split_deque(const string& str,
         deque<string>& tokens,
         const string& delimiters, // default = " "
         int num)                  // default = 0
{
#if 1
  {
    char *p0 = (char*) str.c_str();
    char *p = (char*) str.c_str();
    char *delimiter = (char*) delimiters.c_str();
    char *q = NULL;

    int count = 0;
    while ((q = strstr(p, delimiter)) != NULL) {
        const string &token = str.substr(p-p0, q-p);
        if (num > 0 && ++count >= num) {
            break;
        }
        tokens.push_back(token);
        p = q + delimiters.size();
    }

    if (*p != '\0') {
        const string &token = str.substr(p-p0);
        tokens.push_back(token);
    }
  }
#endif

#if 0
    // Skip delimiters at beginning.
    string::size_type lastPos = str.find_first_not_of(delimiters, 0);
    // Find first "non-delimiter".
    string::size_type pos     = str.find_first_of(delimiters, lastPos);

    int count = 0;
    while (string::npos != pos || string::npos != lastPos) {
        count++;
        if (num != 0 && count >= num) {
            tokens.push_back(str.substr(lastPos, str.size()-lastPos));
            break;
        }

        // Found a token, add it to the vector.
        tokens.push_back(str.substr(lastPos, pos - lastPos));

        // Skip delimiters.  Note the "not_of"
        lastPos = str.find_first_not_of(delimiters, pos);
        // Find next "non-delimiter"
        pos = str.find_first_of(delimiters, lastPos);
    }
#endif
}

// static
bool StrUtil::endsWith(const string &str, const string &x)
{
    int str_size = str.size();
    int x_size = x.size();

    if (str_size < x_size) { return false; }

    int start_pos = str_size - x_size;
    for (int i = 0; i < x_size; i++) {
        if (str[i+start_pos] != x[i]) {
            return false;
        }
    }

    return true;

  #if 0
    string tail = str.substr(str_size-x_size, x_size);
    if (tail == x) {
        return true;
    }

    return false;
  #endif
}

// static
bool StrUtil::endsWithIgnoreCase(const string &str, const string &x)
{
    int str_size = str.size();
    int x_size = x.size();

    if (str_size < x_size) { return false; }

    int start_pos = str_size - x_size;
    for (int i = 0; i < x_size; i++) {
        if (::tolower(str[i+start_pos]) != ::tolower(x[i])) {
            return false;
        }
    }

    return true;

  #if 0
    string tail = str.substr(str_size-x_size, x_size);
    if (StrUtil::tolower(tail) == StrUtil::tolower(x)) {
        return true;
    }
    
    return false;
  #endif
}

// static
bool StrUtil::startsWith(const string &str, const string &x)
{
    if (str.size() < x.size()) { return false; }

    for (int i = 0, n = x.size(); i < n; i++) {
        if (str[i] != x[i]) {
            return false;
        }
    }
    return true;

  #if 0
    return StrUtil::beginsWith(str, x);
  #endif
}

// static
bool StrUtil::beginsWith(const string &str, const string &x)
{
    if (str.size() < x.size()) { return false; }

    for (int i = 0, n = x.size(); i < n; i++) {
        if (str[i] != x[i]) {
            return false;
        }
    }
    return true;

  #if 0
    int str_size = str.size();
    int x_size = x.size();

    if (str_size < x_size) {
        return false;
    }

    string tail = str.substr(0, x_size);
    if (tail == x) {
        return true;
    }

    return false;
  #endif
}

// static
bool StrUtil::startsWithIgnoreCase(const string &str, const string &x)
{
    if (str.size() < x.size()) { return false; }

    for (int i = 0, n = x.size(); i < n; i++) {
        if (::tolower(str[i]) != ::tolower(x[i])) {
            return false;
        }
    }
    return true;

  #if 0
    return StrUtil::beginsWithIgnoreCase(str, x);
  #endif
}

// static
bool StrUtil::beginsWithIgnoreCase(const string &str, const string &x)
{
    for (int i = 0, n = x.size(); i < n; i++) {
        if (::tolower(str[i]) != ::tolower(x[i])) {
            return false;
        }
    }
    return true;

  #if 0
    int str_size = str.size();
    int x_size = x.size();

    if (str_size < x_size) {
        return false;
    }

    string tail = str.substr(0, x_size);
    if (StrUtil::tolower(tail) == StrUtil::tolower(x)) {
        return true;
    }

    return false;
  #endif
}

// static
bool StrUtil::equalsIgnoreCase(const string &s1, const string &s2)
{
    if (s1.size() != s2.size()) { return false; }

    for (int i = 0, n = s1.size(); i < n; i++) {
        if (::tolower(s1[i]) != ::tolower(s2[i])) { return false; }
    }

    return true;
}

// ------------------------------------------------------------------
// 2004/05/04 strstr() 함수의 대소문자 구분없는 버젼을 추가함
//            char *p = StrUtil::strstr_ignorecase(char *str, char *pattern)
// ------------------------------------------------------------------
// 1999/02/02 tolower(), toupper()는 한글에 대해서 시스템마다 다르게 동작
#define toLower(c) (('A'<=(c)&&(c)<='Z')? ((c)-'A'+'a'):(c))
#define toUpper(c) (('a'<=(c)&&(c)<='z')? ((c)-'a'+'A'):(c))

static int strNCaseCmp(char *a, char *b, int n)
{
    assert(a != NULL);
    assert(b != NULL);

    for (int i = 0; i < n; i++) {
        if (toLower(*a) != toLower(*b)) {
            return (toLower(*a) - toLower(*b));
        }
        a++; b++;
    }
    return 0;
}

char *StrUtil::strstrIgnoreCase(const char *str, int m,
                                 const char *pattern, int n)
{
    for (int i = 0; i <= m - n; i++) {
        if (toUpper(str[i]) == toUpper(pattern[0]) &&  /*속도개선*/
            strNCaseCmp((char*)&str[i], (char*)pattern, n) == 0)
        {
            return ((char*)&str[i]);
        }
    }
 
    return (NULL);
}

char *StrUtil::strstrIgnoreCase(const char *str, const char *pattern)
{
    assert(str != NULL);
    assert(pattern != NULL);
 
    return StrUtil::strstrIgnoreCase(str,strlen(str), pattern,strlen(pattern));
}

// 2004-05-19
// 두 스트링을 비교하여, 앞에서 일치하는 최대 길이의 prefix 또는
//                       뒤에서 일치하는 최대 길이의 postfix 구하기

// static
string StrUtil::equalPrefix(const string &s1, const string &s2)
{
    // 두 스트링의 앞부분에서 일치하는 부분을 추출
    // "abcdef" 와 "abxz" 가 입력되면, "ab"를 출력함

    if (s1 == "" || s2 == "") { return ""; }
    assert(s1.size() > 0 && s2.size() > 0);

    int equals_n = 0;

    int short_n = s1.size();
    if ((int)s2.size() < short_n) { short_n = s2.size(); }

    for (int i = 0, n = short_n; i < n; i++) {
        if (s1[i] != s2[i]) {
            return s1.substr(0, equals_n);
        }
        equals_n = i+1;
    }

    if (equals_n > 0) {
        return s1.substr(0, equals_n);
    }

    return "";
}

// static
string StrUtil::equalPostfix(const string &s1, const string &s2)
{
    // 두 스트링의 끝부분에서 일치하는 부분을 추출
    // "abcdef" 와 "sssdef" 가 입력되면, "def"를 출력함

    if (s1 == "" || s2 == "") { return ""; }
    assert(s1.size() > 0 && s2.size() > 0);

    int equals_n = 0;
    int j = s2.size()-1;
    int i = s1.size()-1;

    int short_n = s1.size();
    if ((int)s2.size() < short_n) { short_n = s2.size(); }

    for ( ; i >= 0; i--, j--) {
        if (s1[i] != s2[j]) {
            return s1.substr(s1.size()-equals_n, equals_n);
        }
        equals_n++;
        if (equals_n >= short_n) { break; }
    }

    if (equals_n > 0) {
        return s1.substr(s1.size()-equals_n, equals_n);
    }

    return "";
}




#ifdef STR_UTIL_TEST

#include <cstdio>

void test_1()
{
    printf("test_1() - ");

    string str = "ab cd e";
    vector<string> tokens;

    StrUtil::split(str, tokens, " ", 2);
    assert(tokens[0] == "ab");
    assert(tokens[1] == "cd e");

    printf("ok.\n");
}

void test_1_1()
{
    printf("test_1_1() - ");

    string str = "ab cd e";
    deque<string> tokens;

    StrUtil::split_deque(str, tokens, " ", 2);
    assert(tokens[0] == "ab");
    assert(tokens[1] == "cd e");

    printf("ok.\n");
}

void test_2()
{
    printf("test_2() - ");

    string str = "ab cd e";
    vector<string> tokens;

    StrUtil::split(str, tokens, " ", 1);
    assert(tokens[0] == "ab cd e");

    printf("ok.\n");
}

void test_2_1()
{
    printf("test_2_1() - ");

    string str = "ab cd e";
    deque<string> tokens;

    StrUtil::split_deque(str, tokens, " ", 1);
    assert(tokens[0] == "ab cd e");

    printf("ok.\n");
}

void test_3()
{
    printf("test_3() - ");

    string str = "ab cd e";
    vector<string> tokens;

    StrUtil::split(str, tokens);
    assert(tokens[0] == "ab");
    assert(tokens[1] == "cd");
    assert(tokens[2] == "e");

    printf("ok.\n");
}

void test_3_1()
{
    printf("test_3_1() - ");

    string str = "ab cd e";
    deque<string> tokens;

    StrUtil::split_deque(str, tokens);
    assert(tokens[0] == "ab");
    assert(tokens[1] == "cd");
    assert(tokens[2] == "e");

    printf("ok.\n");
}

void test_4()
{
    printf("test_4() - ");

    string str1 = "ab Cd e";
    string str2 = "ab cd e";
    string str3 = "AB CD E";

    // DEBUG_PRINT("-\n");
    string str4 = StrUtil::tolower(str1);
    assert(str4 == str2);

    // DEBUG_PRINT("-\n");
    string str5 = StrUtil::toupper(str1);
    assert(str5 == str3);

    // DEBUG_PRINT("-\n");
    assert(StrUtil::endsWithIgnoreCase(str1, " E"));
    assert(StrUtil::endsWithIgnoreCase(str1, " e"));
    assert(StrUtil::endsWithIgnoreCase(str1, " d") != true);
    assert(StrUtil::endsWith(str1, " e"));
    assert(StrUtil::endsWith(str1, " E") != true);

    // DEBUG_PRINT("-\n");
    assert(StrUtil::beginsWithIgnoreCase(str1, "ab "));
    assert(StrUtil::beginsWithIgnoreCase(str1, "AB "));
    assert(StrUtil::beginsWithIgnoreCase(str1, "abc") != true);
    assert(StrUtil::beginsWith(str1, "ab "));
    assert(StrUtil::beginsWith(str1, "AB ") != true);

    printf("ok.\n");
}

void test_5()
{
    printf("test_5() - ");

    string str1 = "ab  c  \r\r";
    string str2 = "ab  c";
    string str3 = "ab  c  ";

    assert(StrUtil::trim(str1) == str2);
    assert(StrUtil::trim_crlf(str1) == str3);
    
    printf("ok.\n");
}

void test_6()
{
    printf("test_6() - ");

    string str = "ab cdEf ghi";

    int pos = StrUtil::findIgnoreCase(str, "ef");

    // DEBUG_PRINT("pos: %d\n", (int)pos);

    assert(pos == 5);

    int pos2 = StrUtil::findIgnoreCase(str, "dd");

    assert(pos2 == -1);

    printf("ok.\n");
}

void test_7()
{
    printf("test_7() - ");

    string s1 = "37";
    int i1 = 37;

    string s2 = StrUtil::int2string(i1);
    int i2 = StrUtil::string2int(s1);

    assert(i1 == i2);
    assert(s1 == s2);

    printf("ok.\n");
}

void test_8()
{
    printf("test_8() - ");

    string s1 = " 37\t \r x \n";

    string s2 = StrUtil::trim_blanks(s1);

    assert(s2 == "37 x");

    printf("ok.\n");
}

void test_9()
{
    printf("test_9() - ");

    string s1 = " abc d ";
    string s2 = " abx d ";
    string s3 = " abC d ";

    assert(! StrUtil::equalsIgnoreCase(s1, s2));
    assert(StrUtil::equalsIgnoreCase(s1, s3));

    printf("ok.\n");
}

void test_10()
{
    printf("test_10() - ");

    string str = "ab cd e";

    vector<string> tokens = StrUtil::split(str, " ");

    assert(tokens[0] == "ab");
    assert(tokens[1] == "cd");
    assert(tokens[2] == "e");

    vector<string> t2 = StrUtil::split(str, " ", 2);
    assert(t2.size() == 2);
    assert(t2[0] == "ab");
    assert(t2[1] == "cd e");

    printf("ok.\n");
}

void test_10_1()
{
    printf("test_10_1() - ");

    string str = "ab cd e";

    deque<string> tokens = StrUtil::split_deque(str, " ");

    assert(tokens[0] == "ab");
    assert(tokens[1] == "cd");
    assert(tokens[2] == "e");

    deque<string> t2 = StrUtil::split_deque(str, " ", 2);
    assert(t2.size() == 2);
    assert(t2[0] == "ab");
    assert(t2[1] == "cd e");

    printf("ok.\n");
}


void test_11()
{
    printf("test_11() - ");

    string str1 = "ab cd e";
    vector<string> tokens = StrUtil::split(str1, " ");

    string str2 = StrUtil::join(" ", tokens);
    if (! (str2 == str1)) {
        cout << "str1: [" << str1 << "]" << endl;
        cout << "str2: [" << str2 << "]" << endl;
    }
    assert(str2 == str1);

    printf("ok.\n");
}

void test_12()
{
    printf("test_12() - ");

    string str1 = "ab cd xe eexez yxe";
    string str2 = StrUtil::replace(str1, "xe", "YYY");

    if (str2 != "ab cd YYY eeYYYz yYYY") {
        printf("%s\n", str2.c_str());
    }

    assert(str2 == "ab cd YYY eeYYYz yYYY");
    printf("ok.\n");
}

void test_13()
{
    printf("test_13() - ");

    // 스트링이 1개 밖에 없을 때, 또는 0개 있을 때,
    // join 연산을 하면, glue 가 전혀 사용되지 않아야 한다.

    string abc = "abc";
    vector<string> vect;

    string joined1 = StrUtil::join(" ", vect);
    assert(joined1 == "");

    vect.push_back(abc);
    string joined2 = StrUtil::join(" ", vect);
    assert(joined2 == "abc");

    vect.push_back(abc);
    string joined3 = StrUtil::join(" ", vect);
    assert(joined3 == "abc abc");

    printf("ok.\n");
}

void test_14()
{
    printf("test_14() - ");

    string s1 = "abc";
    string s2 = "aBc";
    string s3 = "aBcc";
    string s4 = "aBcy";

    assert(StrUtil::equalsIgnoreCase(s1, s2));
    assert(StrUtil::equalsIgnoreCase(s2, s2));
    assert(! StrUtil::equalsIgnoreCase(s2, s3));
    assert(! StrUtil::equalsIgnoreCase(s3, s4));

    printf("ok.\n");
}

void test_15()
{
    printf("test_15() - ");

    string s1 = "abc.def";
	string p1 = "abc.*";
	string p2 = "abc????";
	string p3 = "abc???*";
	string p4 = "abc??*?";
	string p5 = "a.c??*?";

	assert(StrUtil::simpleMatch(s1, p1) == true);
	assert(StrUtil::simpleMatch(s1, p2) == true);
	assert(StrUtil::simpleMatch(s1, p3) == true);
	assert(StrUtil::simpleMatch(s1, p4) == true);
	assert(StrUtil::simpleMatch(s1, p5) == false);

	printf("ok.\n");
}

void test_16()
{
    printf("test_16() - ");

    string s1 = "fdkslajf skfljdsakl fdjsaf dsjaklk1%^@#$fklasj ZZ";
    string u1 = "!@#$%%^&*()_+=-";

    string s2 = StrUtil::trim_undesirable(s1, u1);

    assert(s2 == string("fdkslajf skfljdsakl fdjsaf dsjaklk1fklasj ZZ"));

    printf("ok.\n");
}

void test_17()
{
    printf("test_17() - ");

  {
    string s = "\na\n\nb\n\n";
    vector<string> a = StrUtil::split(s, "\n");
    assert(a.size() == 5);
    assert(a[0] == string(""));
    assert(a[1] == string("a"));
    assert(a[2] == string(""));
    assert(a[3] == string("b"));
    assert(a[4] == string(""));
  }

  {
    string s = "a\nb\n";
    deque<string> a = StrUtil::split_deque(s, "\n");
    assert(a.size() == 2);
    assert(a[0] == string("a"));
    assert(a[1] == string("b"));
  }

  {
    string s = "a\n\n";
    deque<string> a = StrUtil::split_deque(s, "\n");
    assert(a.size() == 2);
    assert(a[0] == string("a"));
    assert(a[1] == string(""));
  }

    printf("ok.\n");
}


string __tolower1(const string &str)
{
    string tmp = str;

    for (int i = 0, n = tmp.size(); i < n; i++) {
        *((char*)(&tmp[i])) = tolower(tmp[i]);
    }

    return tmp;
}

string __tolower2(const string &str)
{
    string tmp = str;

    transform(tmp.begin(), tmp.end(), tmp.begin(), (int(*)(int)) ::tolower);

    return tmp;
}

#include <time.h>

void test_x()
{
    string str1 = "fdaf fafDSJKALFJ Fdkaslfd abckdls0fdkslaajfklafjdkfd "
                  "afd asfdas fd aXBX fdaklfjdsaf";

    int num_count = 1000000;

    time_t t0 = time(NULL);

    for (int i = 0; i < num_count; i++) {
        string a = __tolower1(str1);
    }

    time_t t1 = time(NULL);

    for (int i = 0; i < num_count; i++) {
        string a = __tolower2(str1);
    }

    time_t t2 = time(NULL);

    printf("diff1: %d, diff2: %d\n", (int)(t1-t0), (int)(t2-t1));
}

void test_18()
{
    printf("test_18() - ");
    string email = "hiongun@mobigen.com";

    vector<string> array = StrUtil::split(email, "@", 2);
    assert(array.size() == 2);
    assert(array[0] == string("hiongun"));
    assert(array[1] == string("mobigen.com"));

    printf("ok.\n");
}

void test_19()
{
    printf("test_19() - ");

  {
    string str = "hiongun@mobigen.com";
    string pattern = "moBIgen";

    char *p = strstr(str.c_str(), string("mobigen").c_str());
    char *p2 = StrUtil::strstrIgnoreCase(str.c_str(), pattern.c_str()); 

    assert(p == p2);

    assert(StrUtil::strstrIgnoreCase(str.c_str(), string("XX").c_str())==NULL);
  }

    printf("ok.\n");
}

void test_20()
{
    printf("test_20() - "); fflush(stdout);

  {
    string str;
    string pattern = "moBIgen";

    vector<string> rets = StrUtil::split(str, pattern);
    // DEBUG_PRINT("RETS size = %d\n", rets.size());
  }

    printf("ok.\n");
}

void test_21()
{
    printf("test_21() - "); fflush(stdout);

  {
    string s1 = "2.13";
    float f1 = StrUtil::string2float(s1);

    if (! (float(f1) == float(2.13))) {
        DEBUG_PRINT("f1: %.20f\n", f1);
        DEBUG_PRINT("s1: %s\n", s1.c_str());
    }
    assert(float(f1) == float(2.13));

    float f2 = 1.157;
    string s2 = StrUtil::float2string(f2, 3);
    assert(s2 == string("1.157"));
  }

    printf("ok.\n");
}

void test_22()
{
    printf("test_22() - "); fflush(stdout);
  {
    string s1 = "";
    s1 = StrUtil::trim_crlf(s1);

    assert( s1.length() == 0 );
  }
    printf("ok.\n");

}

void test_23()
{
    printf("test_23() - "); fflush(stdout);
  {
    string s1 = "abcxxx";
    string s2 = "abcdeefkalj";
    string s3 = StrUtil::equalPrefix(s1, s2);
    assert(s3 == string("abc"));
  }

  {
    string s1 = "abcdeefkalj";
    string s2 = "abcxxx";
    string s3 = StrUtil::equalPrefix(s1, s2);
    assert(s3 == string("abc"));
  }

  {
    string s1 = "abcxxx";
    string s2 = "xbcdeefkalj";
    string s3 = StrUtil::equalPrefix(s1, s2);
    assert(s3 == string(""));
  }

  {
    string s1 = "abcxzx";
    string s2 = "abcdeefcxzx";
    string s3 = StrUtil::equalPostfix(s1, s2);
    if (! (s3 == string("cxzx"))) {
        DEBUG_PRINT("s3: [%s]\n", s3.c_str());
    }
    assert(s3 == string("cxzx"));
  }

  {
    string s1 = "abcdeefcxzx";
    string s2 = "abcxzx";
    string s3 = StrUtil::equalPostfix(s1, s2);
    if (! (s3 == string("cxzx"))) {
        DEBUG_PRINT("s3: [%s]\n", s3.c_str());
    }
    assert(s3 == string("cxzx"));
  }

  {
    string s1 = "abcxzz";
    string s2 = "abcdeefcxzx";
    string s3 = StrUtil::equalPostfix(s1, s2);
    assert(s3 == string(""));
  }

    printf("ok.\n");
}

void test_24()
{
     printf("test_24() - "); fflush(stdout);

   {
     string str1 = "ffkdlsajflfjdsl";
     string str2 = StrUtil::replaceFirst(str1, str1.substr(0,1), "A");
     assert(str2 == "Afkdlsajflfjdsl");
   }

   {
     string str1 = "ffkdXsaXflfjdsl";
     string str2 = StrUtil::replaceFirst(str1, "X", "A");
     assert(str2 == "ffkdAsaXflfjdsl");
   }

     printf("ok.\n");
}

void test_25()
{
     printf("test_25() - "); fflush(stdout);

   {
     string str1 = "aaabbb";
     string str2 = StrUtil::ca2sp(str1);
     assert(str2 == "aaa  bbb");
   }

   {
     string str1("ffkd\1X\2xx", 9);
     string str2 = StrUtil::ca2sp(str1);
     assert(str2 == "ffkd X xx");
   }

     printf("ok.\n");
}


void test_26()
{
     printf("test_26() - "); fflush(stdout);

   {
     // 매우 큰 string으로 join()호출할 경우,
     // stack overflow 날 수가 있음. join하는 결과 스트링은
     // 스택이 아닌, 실시간 allocation되어야 함.
     vector<string> tokens;
     for (int i = 0; i < 100000; i++) {
         tokens.push_back("------------------------------");
     }
     string joined = StrUtil::join(",", tokens);
   }

   {
     // 매우 큰 string으로 join_deque()호출할 경우,
     // stack overflow 날 수가 있음. join하는 결과 스트링은
     // 스택이 아닌, 실시간 allocation되어야 함.
     deque<string> tokens;
     for (int i = 0; i < 100000; i++) {
         tokens.push_back("------------------------------");
     }
     string joined = StrUtil::join_deque(",", tokens);
   }

     printf("ok.\n");
}

int main()
{
    test_1();
    test_1_1();
    test_2();
    test_2_1();
    test_3();
    test_3_1();
    test_4();
    test_5();
    test_6();
    test_7();
    test_8();
    test_9();
    test_10();
    test_10_1();
    test_11();
    test_12();
    test_13();
    test_14();
    test_15();
    test_16();
    test_17();
    test_18();
    test_19();
    test_20();
    test_21();
    test_22();
    test_23();
    test_24();
    test_25();
    test_26();

    // test_x();

    return 0;
}

#endif // STR_UTIL_TEST
