import API.M6 as M6
import xml.etree.ElementTree as ET

def main():
    doc = ET.parse('conf/IS.xml')
    root = doc.getroot()
    host = root.find("Summary").find("Sum_info").find("Connection").attrib['url']
    host = host.split('://')[1]
    user = root.find("Summary").find("Sum_info").find("Connection").attrib['user']
    pwd = root.find("Summary").find("Sum_info").find("Connection").attrib['pass']

    conn = M6.Connection(host, user, pwd)
    c = conn.Cursor()

    q = '''
            CREATE TABLE MSF_TEST_TABLE_MAIN(
                k           TEXT,
                p           TEXT,
                INCOME      TEXT,
                EXPENSES    TEXT
            )
            datascope       LOCAL
            ramexpire       30
            diskexpire      34200
            partitionkey    k
            partitiondate   p
            partitionrange  10
            ;
        '''
    c.Execute2(q)
    c.SetFieldSep('|^|')
    c.SetRecordSep('\n')

    c.Load('MSF_TEST_TABLE_MAIN',
           'k', '20180615000000',
           'data/MSF_TEST_TABLE_MAIN.ctl',
           'data/MSF_TEST_TABLE_MAIN_0.dat')

    c.Load('MSF_TEST_TABLE_MAIN',
           'k', '20180615001000',
           'data/MSF_TEST_TABLE_MAIN.ctl',
           'data/MSF_TEST_TABLE_MAIN_1.dat')

    c.Load('MSF_TEST_TABLE_MAIN',
           'k', '20180615002000',
           'data/MSF_TEST_TABLE_MAIN.ctl',
           'data/MSF_TEST_TABLE_MAIN_2.dat')

    c.Load('MSF_TEST_TABLE_MAIN',
           'k', '20180615003000',
           'data/MSF_TEST_TABLE_MAIN.ctl',
           'data/MSF_TEST_TABLE_MAIN_3.dat')

    c.Close()
    conn.close()

if __name__ == '__main__':
    main()
