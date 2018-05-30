#ifndef __PthMsg_h__
#define __PthMsg_h__

class PthMsg
{
  private:
    int qid;
    bool error;
    string errstr;

  public: 
    bool isError();

  public:
    bool init(int key = 0);

    PthMsg(int key = 0);
    ~PthMsg();

  public:
    bool send(long int type, const string &str, int timeout = 0);
    bool recv(long int type, string &str, int timeout = 0);

  public:
    bool remove();
};

#endif // __PthMsg_h__
