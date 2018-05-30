#ifndef _MD5_c_
#define _MD5_c_

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <assert.h>

#include <string>

#include "MD5LIB.h"
#include "MD5.h"

using namespace std;

// static
void MD5::encode(const char *string, char *digest_str)
{
    MD5LIB context;
    unsigned int len = strlen ( (char *)string);

    context.update   ((unsigned char*)string, len);
    context.finalize ();

    context.get_hex_digest(context, digest_str);
}

// static
char *MD5::encode(const char *string) // thread_unsafe !!
{
    static char digest_str[128];
    memset(digest_str, 0x00, sizeof(digest_str));

    MD5::encode(string, digest_str);

    return digest_str;
}

// static
void MD5::encode(const char *string, int length, char *digest_str)
{
    MD5LIB context;
    unsigned int len = length;

    context.update   ((unsigned char*)string, len);
    context.finalize ();

    context.get_hex_digest(context, digest_str);
}

// static
void MD5::encode(const string &string, string &sDigest)
{
    static char digest_str[128];
    memset(digest_str, 0x00, sizeof(digest_str));

    MD5LIB context;
    unsigned int len = string.size();

    context.update   ((unsigned char*)string.c_str(), len);
    context.finalize ();

    context.get_hex_digest(context, digest_str);

    sDigest = digest_str;
}

// static
string MD5::encode(const string &str)
{
    char digest_str[128];
    memset(digest_str, 0x00, sizeof(digest_str));

    MD5LIB context;
    unsigned int len = str.size();

    context.update   ((unsigned char*)str.c_str(), len);
    context.finalize ();

    context.get_hex_digest(context, digest_str);

    string sDigest = digest_str;

    return sDigest;
}

#ifdef MD5_TEST
/*
int main()
{
    char digest_str[128];
    memset(digest_str, 0x00, sizeof(digest_str));

    string input = "yjh125";
  {
    MD5::encode(input.c_str(), digest_str);
    assert(strcmp(digest_str, "75b1de0f802c125b7e595504910bc27c") == 0);
    printf("%s\n", digest_str);
  }
  {
    char* digest_str = MD5::encode(input.c_str());
    assert(strcmp(digest_str, "75b1de0f802c125b7e595504910bc27c") == 0);
    printf("%s\n", digest_str);
  }
  {
    MD5::encode(input.c_str(), input.size(), digest_str);
    assert(strcmp(digest_str, "75b1de0f802c125b7e595504910bc27c") == 0);
    printf("%s\n", digest_str);
  }
  {
    string output;
    MD5::encode(input, output);
    assert(output == "75b1de0f802c125b7e595504910bc27c");
    printf("%s\n", output.c_str());
  }
  {
    string output;
    output = MD5::encode(input);
    assert(output == "75b1de0f802c125b7e595504910bc27c");
    printf("%s\n", output.c_str());
  }
}
*/


int main(int argc, char *argv[])
{
    if (argc != 2) {
        printf("Usage: %s string\n", argv[0]);
        exit(0);
    }

    char *result = MD5::encode(argv[1]);
    printf("%s: %s\n", argv[1], result);
}


#endif // MD5_TEST

#endif // _MD5_c_
