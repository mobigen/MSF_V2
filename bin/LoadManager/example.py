import cx_Oracle
import API.M6 as M6
import ConfigParser

def main():
    conf = ConfigParser.ConfigParser()
    conf.read('conf/TEST.conf')
    db = conf.get('GENERAL', 'SRC_DBMS')
    host = conf.get('GENERAL', 'SRC_IP')
    port = conf.get('GENERAL', 'SRC_PORT')
    sid = conf.get('GENERAL', 'SRC_DB')
    user = conf.get('GENERAL', 'SRC_ID')
    pwd = conf.get('GENERAL', 'SRC_PWD')

    conn = cx_Oracle.connect('%s/%s@%s:%s/%s' % \
            (user, pwd, host, port, sid))
    curs = conn.cursor()

    curs.execute('''
            create table TEST_TABLE(
                k varchar(20),
                p varchar(20),
                a varchar(20))''')
    conn.commit()

    curs.execute("INSERT INTO TEST_TABLE (k, p, a) \
                  VALUES ('k3', '20110616000000', '1.2')")
    curs.execute("INSERT INTO TEST_TABLE (k, p, a) \
                  VALUES ('k4', '20110616000000', '0')")
    curs.execute("INSERT INTO TEST_TABLE (k, p, a) \
                  VALUES ('k5', '20110616000000', '0.1')")
    conn.commit()
    conn.close()

    conn = M6.Connection('192.168.101.104:5050','vsfs', 'vsfs123')
    curs = conn.Cursor()
    q = '''
            CREATE TABLE TEST_TABLE (
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
        '''

    curs.Execute2(q)

    curs.close()
    conn.close()


if __name__ == '__main__':
    main()
