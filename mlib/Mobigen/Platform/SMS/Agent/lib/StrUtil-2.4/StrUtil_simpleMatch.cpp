#include <stdio.h>

#include "StrUtil.h"

#ifndef DEBUG_PRINT
#  ifdef NDEBUG
#    define DEBUG_PRINT if (0) printf
#  else
#    define DEBUG_PRINT printf("(%s,%d) ", __FILE__, __LINE__); printf
#  endif // NDEBUG
#endif // DEBUG_PRINT

bool StrUtil::simpleMatch(const string &strIn, const string &patternIn)
{
    char *str = (char*)strIn.c_str();
	char *pattern = (char*)patternIn.c_str();

  runPatternMatchAgain:
    if (str[0] == '\0' && pattern[0] == '\0') {
        // DEBUG_PRINT("return true\n");
        return true;
    } else if (str[0] == '\0') {
        if (pattern[0] == '*') {
           if (pattern[1] == '\0') {
                // DEBUG_PRINT("return true\n");
                return true;
           } else {
                // REMOVE_TAIL_RECURSION
                // return strPatternMatch(str, &pattern[1]);
                pattern++;
                goto runPatternMatchAgain;
           }
        } else {
            // DEBUG_PRINT("return false\n");
            return false;
        }
    } else if (pattern[0] == '\0') {
        // DEBUG_PRINT("return false\n");
        return false;
    }

    if (pattern[0] == '?') {
        if (str[0] != '\0') {
            // DEBUG_PRINT("return strPatternMatch('%s','%s')\n",
            //  &str[1], &pattern[1]);
              
            // REMOVE_TAIL_RECURSION
            // return (strPatternMatch(&str[1], &pattern[1]));

            str++;
            pattern++;
            goto runPatternMatchAgain;
        } else {
            // DEBUG_PRINT("return false\n");
            return false;
        }
    } else if (pattern[0] == '*') {
        int i, len = strlen(str);

        for (i = 1; i <= len; i++) {
            // DEBUG_PRINT("try strPatternMatch('%s','%s')\n",
            //    &str[i], &pattern[1]);

            if (StrUtil::simpleMatch(&str[i], &pattern[1])) {
                // DEBUG_PRINT("return true\n");
                return true;
            }
        }

        return false;
    } else if (str[0] == pattern[0]) {
        // DEBUG_PRINT("return strPatternMatch('%s','%s')\n", 
        //   &str[1], &pattern[1]);

        // REMOVE_TAIL_RECURSION
        // return (strPatternMatch(&str[1], &pattern[1]));
        str++;
        pattern++;
        goto runPatternMatchAgain;

        // 1999/02/11 패턴에 별표('*')와 물음표('?')를 입력 할 수 있도록,
        //             '\\'를 이용하여 escape시킬 수 있도록 함.

    } else if (pattern[0] == '\\' && ((pattern[1] == '*' && str[0] == '*') ||
          (pattern[1] == '?' && str[0] == '?')))
    {
        str++;
        pattern += 2;
        goto runPatternMatchAgain;
    }

    // DEBUG_PRINT("return false\n");
    return false;
}
