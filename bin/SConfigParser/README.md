# SConfigParser

고객측의 요구에 따라 Config file을 암호화 할 일이 있을 수 있습니다.

Key를 생성하고 암호화를 하고 복호화를 하는 과정을 편하게 사용 할 수 있도록 하는 목적이 있습니다.

암호화된 Config file을 불러올때는 파이썬 내장 모듈인 ConfigParser가 사용하는 메소드와 최대한 동일하게 작성하여 혼동의 여지가 없도록 하였습니다.

## How to use
### 암호화를 위한 Key 생성하기
```Bash
$ python KeyGenerator.py > [저장할 파일 경로]
```

**Example**
키 생성하는 예제를 보겠습니다.
```Bash
$ python KeyGenerator.py > key/TestKey
$ cat key/TestKey
WawJqJ1ifoJmoxApg1qwPvixtDajroiPUB7VzH2MVv0=
```
키는 생성될 때마다 매번 달라집니다.

### 암호화 되어 있지 않은 Config 암호화하기
```Bash
$ python SConfigParser.py <Key> <ConfigFilePath> <Path gonna be saved as encrypted>
```

**Example**
생성된 키를 이용해서 MySQL.conf를 암호화 하는 예제를 보겠습니다.

기존의 MySQL.conf 입니다.
```Bash
$ cat conf/MySQL.conf
[TEST]
HOST=192.168.100.16
PORT=3306
ID=mfs
PWD=hellomfs
DB=test
```

앞에서 생성한 Key를 이용하여 암호화 하는 방법과 암호화된 Config file 입니다.
```Bash
$ python SConfigParser.py key/TestKey conf/MySQL.conf conf/MySQL.conf.enc
$ cat conf/MySQL.conf.enc
gAAAAABbRudgI9l9wbpzsDcsN2kv4vNyrOQ7yQ_yblTZeOPST1gTnscdIN1KaqX9ktYmrAMRFkjOZjkenS2fM2ieWzWS-qRe9jzyJrhFPA89ffkdP-UhN_kFpvovk_hm2IB_mo3asrHWfzJFbqxSpgaa4xnI27RhU7Je777QDyPRMLX_Ei_o08GcdjUOw66qOGmrQw8olYvIrbcBf9byyVZ3chSalLsIsg==
```

Python 코드내에서 암호화된 config를 가져오는 방법입니다.
```Python
import SConfigParser

sconf = SConfigParser.SConfigParser()
sconf.read('conf/MySQL.conf.enc', 'key/TestKey')
print sconf.cfg
```
print된 결과입니다.
```
{'TEST': {'id': 'mfs', 'host': '192.168.100.16', 'db': 'test', 'pwd': 'hellomfs', 'port': '3306'}}
```

## Methods
ConfigParser.ConfigParser 클래스에서 제공하는 메소드와 동일합니다만 자주쓰는 일부분의 메소드만 제공됩니다.

|method     |parameters        |parameter discription|return type|return|
|:---------:|:----------------:|---------------------|:---------:|:-----:|
|read       |path      | 암호화된 ConfigFile 의 path|No retrun||
|           |keypath   | 암호화된 ConfigFile을 복호화할 Key파일의 경로|||
|get        |ConfigParser와 동일||||
|sections   |ConfigParser와 동일||||
|getint     |ConfigParser와 동일||||
|getboolean |ConfigParser와 동일||||
|has_section|ConfigParser와 동일||||
|has_option |ConfigParser와 동일||||

## Attributes
|attribute|return type|return description|
|:-------:|:---------:|------------------|
|cfg      |object     |jsonified config  |
