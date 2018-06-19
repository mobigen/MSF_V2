import MySQLdb
import Mobigen.Common.Log as Log; Log.Init()

class MySQLHandler:
    def __init__(self, section, Parser):
        self.mHost  = Parser.get(section, 'HOST')
        self.mUser  = Parser.get(section, 'ID')
        self.mPass  = Parser.get(section, 'PWD')
        self.mDatabase = Parser.get(section, 'DB')
        self.mPort  = Parser.get(section, 'PORT')
        self.connect()

    def __del__(self):
        self.disconnect()

    def connect(self):
        try:
            self.Conn = MySQLdb.connect(self.mHost,
                                        self.mUser,
                                        self.mPass,
                                        self.mDatabase,
                                        int(self.mPort))
            self.Conn.set_character_set('UTF8')
            self.Curs = self.Conn.cursor()
        except MySQLdb.OperationalError:
            __LOG__.Exception()
            self.Conn = None

    def disconnect(self):
        if self.Curs != None:
            try:
                self.Curs.close()
            except MySQLdb.ProgrammingError:
                pass
            finally:
                pass

        if self.Conn != None:
            try :
                self.Conn.close()
            except MySQLdb.ProgrammingError:
                pass
            finally:
                pass

        __LOG__.Trace('DB Disconnect!!')

    def executeGetData(self, sql, retry=0):
        data = None
        try :
            __LOG__.Trace(sql)
            self.Curs.execute(sql)
            data = self.Curs.fetchall()
            self.Conn.commit()
        except MySQLdb.ProgrammingError as exc:
            retry += 1
            __LOG__.Exception()
            __LOG__.Trace(exc.args)
            if exc.args[0] == 'cursor closed':
                #retry for timeout
                self.connect()
                if retry < 3:
                    data = self.executeGetData(sql,retry)
            else:
                data = False
        except MySQLdb.OperationalError as exc:
            retry += 1
            __LOG__.Exception()
            __LOG__.Trace(exc.args)
            self.connect()
            if retry < 3:
                data = self.executeGetData(sql, retry)
            else:
                data = False
        return data

    def executeQuery(self, sql, retry=0):
        try :
            self.Curs.execute(sql)
            self.Conn.commit()
            return True
        except MySQLdb.ProgrammingError as exc:
            retry += 1
            __LOG__.Exception()
            __LOG__.Trace(exc.args)
            if exc.args[0] == 'cursor closed':
                #retry for timeout
                self.connect()
                if retry < 3:
                    return self.executeQuery(sql, retry)
                return False
            __LOG__.Trace("EXECUTE ERROR SQL : %s.." % sql)
            self.Conn.rollback()
            return False
        except MySQLdb.OperationalError as exc:
            retry += 1
            __LOG__.Exception()
            __LOG__.Trace(exc.args)
            self.connect()
            if retry < 3:
                return self.executeQuery(sql, retry)
            return False
