import cx_Oracle
import Mobigen.Common.Log as Log; Log.Init()

class OracleHandler:
    def __init__(self, section, Parser):
        self.Host = Parser.get(section, 'HOST')
        self.User = Parser.get(section, 'ID')
        self.Pass = Parser.get(section, 'PWD')
        self.Sid = Parser.get(section, 'SID')
        self.Port = Parser.get(section, 'PORT')
        self.connect()

    def __del__(self):
        self.disconnect()

    def connect(self):
        try:
            self.Conn = cx_Oracle.connect('%s/%s@%s:%s/%s' % \
                        (self.User, self.Pass, self.Host, self.Port, self.Sid))
            self.Curs = self.Conn.cursor()
        except cx_Oracle.DatabaseError:
            __LOG__.Exception()
            self.Conn = None

    def disconnect(self):
        if self.Curs != None:
            try:
                self.Curs.close()
            except cx_Oracle.InterfaceError:
                pass
            finally:
                pass

        if self.Conn != None:
            try:
                self.Conn.close()
            except cx_Oracle.DatabaseError:
                pass
            finally:
                pass

        __LOG__.Trace('DB Disconnect!!')

    def executeGetData(self, sql, retry=0):
        data = None
        try:
            __LOG__.Trace(sql)
            self.Curs.execute(sql)
            data = self.Curs.fetchall()
            self.Conn.commit()
        except cx_Oracle.DatabaseError as exc:
            err, = exc.args
            retry += 1
            __LOG__.Exception()
            __LOG__.Trace(err.message)
            if err.code == 12170:
                # retry for timeout
                self.connect()
                if retry < 3:
                    data = self.executeGetData(sql, retry)
            else:
                data = False
        except cx_Oracle.InterfaceError as exc:
            retry += 1
            err, = exc.args
            __LOG__.Exception()
            __LOG__.Trace(err.message)
            self.connect()
            if retry < 3:
                data = self.executeGetData(sql, retry)
            else:
                data = False

        return data

    def executeQuery(self, sql, retry=0):
        try:
            self.Curs.execute(sql)
            self.Conn.commit()
            return True
        except cx_Oracle.DatabaseError as exc:
            err, = exc.args
            retry += 1
            __LOG__.Exception()
            __LOG__.Trace(err.message)
            if err.code == 12170:
                # retry for timeout
                self.connect()
                if retry < 3:
                    return self.executeQuery(sql, retry)
                return False
            __LOG__.Trace("EXECUTE ERROR SQL : %s.." % sql)
            self.Conn.rollback()
            return False
        except cx_Oracle.InterfaceError as exc:
            retry += 1
            err, = exc.args
            __LOG__.Exception()
            __LOG__.Trace(err.message)
            self.connect()
            if retry < 3:
                return self.executeQuery(sql, retry)
            return False

