#ifndef _MD5_h_
#define _MD5_h_

#include <string>

using namespace std;

class MD5 {
  public:
    static char *encode(const char *str);
    static void encode(const char *str, char *digest_str_32_bytes);
    static void encode(const char *str, int len, char *digest_str_32_bytes);
    static void encode(const string &string, string &digest);
    static string encode(const string &string);
};

#endif // _MD5_h_
