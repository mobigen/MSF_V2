# coding: utf-8
import os
import sys
import lib.M6 as M6

table_name = 'TB_NEWS_MINING'

obj = sys.argv[1].strip().lower()  # "prd or dev"

if obj == 'prd':
    import ddl.connection_info_prd as info
elif obj == 'dev':
    import ddl.connection_info_dev as info

command = sys.argv[2].strip().lower()  # "create or drop or delete"
option = sys.argv[3].strip().lower()  # "table or index or backend or row"

if command == 'drop' and option == 'backend':
    greater_than = sys.argv[4].strip().lower()  # 20190101000000
    less_than = sys.argv[5].strip().lower()  # 20190201000000
    try:
        iris_key = sys.argv[6].strip()  # 0
    except:
        iris_key = None

if command == 'delete' and option == 'row':
    where = sys.argv[4].strip().lower()  # CREATE_DT >= 20190101000000 AND IRIS_KEY = 1
    greater_than = sys.argv[5].strip().lower()  # 20190101000000
    less_than = sys.argv[6].strip().lower()  # 20190201000000
    try:
        iris_key = sys.argv[7].strip()  # 0
    except:
        iris_key = None

conn = M6.Connection(info.host, info.user_id, info.user_passwd, Direct=info.direct, Database=info.database)
c = conn.Cursor()
c.SetFieldSep('|^|')
c.SetRecordSep('|^-^|')

sql = []

if command == 'create' and option == 'table':
    sql.append('''
            CREATE VIRTUAL TABLE {table_name} USING fts4 (
            UUID TEXT,
            DOMAIN TEXT,
            URL TEXT,
            KEYWORD TEXT,
            TOP_SENTENCE TEXT,
            TOP_WORD TEXT,
            SENTENCES TEXT,
            WORDS TEXT,
            TEXT TEXT,
            BODY TEXT,
            DATE TEXT,
            SECTION TEXT,
            PDATE TEXT,
            NOTINDEXED=KEYWORD,
            NOTINDEXED=TOP_SENTENCE,
            NOTINDEXED=TOP_WORD,
            NOTINDEXED=TEXT )
            datascope       LOCAL
            ramexpire       1440
            diskexpire      103680000
            partitionkey    SECTION
            partitiondate   PDATE
            partitionrange  1440;
        ''')

elif command == 'create' and option == 'index':
    pass

elif command == 'drop' and option == 'table':

    sql.append("drop table {table_name};")

elif command == 'drop' and option == 'index':
    pass

elif command == 'drop' and option == 'backend':

    if iris_key:
        plus = 'AND KEY = %s' % iris_key
    else:
        plus = ''

    sql.append(("drop backend {table_name} ( %s <= PARTITION AND PARTITION < %s %s) ;" % (greater_than, less_than, plus)).encode('utf-8').decode("unicode-escape"))

elif command == 'delete' and option == 'row':

    if iris_key:
        plus = 'AND KEY = %s' % iris_key
    else:
        plus = ''

    sql.append(("/*+ LOCATION ( %s <= PARTITION AND PARTITION < %s %s) */ delete from {table_name} where %s ;" % (greater_than, less_than, plus, where)).encode('utf-8').decode("unicode-escape"))

for q in sql:
    q = q.format(table_name=table_name)
    sys.stderr.write("%s %s\n" % (c.Execute2(q), q))
    sys.stderr.flush()

c.Close()
conn.close()
