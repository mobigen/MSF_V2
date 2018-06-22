import API.M6 as M6
import ConfigParser
import sys

def main():
    conf = ConfigParser.ConfigParser()
    conf.read(sys.argv[1])
    host = conf.get('IRIS', 'IRIS_IP').strip()
    user = conf.get('IRIS', 'IRIS_ID').strip()
    pwd = conf.get('IRIS', 'IRIS_PWD').strip()
    tbl = conf.get('IRIS', 'TABLE').strip()

    conn = M6.Connection(host, user, pwd)
    c = conn.Cursor()
    c.SetFieldSep('|^|')
    c.SetRecordSep('\n')

    q = '''
    CREATE TABLE %s (
       k         TEXT,
       p         TEXT,
       a         TEXT
    )
    datascope       LOCAL
    ramexpire       30
    diskexpire      34200
    partitionkey    k
    partitiondate   p
    partitionrange  10
    ;
    ''' % tbl

    print c.Execute2(q)

    c.Close()
    conn.close()

if __name__ == '__main__':
    main()
