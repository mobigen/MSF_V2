import signal
import logging
import urllib
import shutil
import datetime as dt
import json
import time
import os
import traceback
from logging import handlers

import API.M6 as M6
from common_info import iris_conn, log_info

from java.nio.charset import StandardCharsets
from org.apache.nifi.components.state import Scope
from org.apache.commons.io import IOUtils
from org.apache.nifi.processor.io import StreamCallback, InputStreamCallback, OutputStreamCallback

import API.M6 as M6
import traceback

#---------------------------------------------------------------------------------------------------------------
def getTracebackStr():
    lines = traceback.format_exc().strip().split('\n')
    rl = [lines[-1]]
    lines = lines[1:-1]
    lines.reverse()
    nstr = ''
    for i in range(len(lines)):
        line = lines[i].strip()
        if line.startswith('File "'):
            eles = lines[i].strip().split('"')
            basename = os.path.basename(eles[1])
            lastdir = os.path.basename(os.path.dirname(eles[1]))
            eles[1] = '%s/%s' % (lastdir,basename)
            rl.append('^\t%s %s' % (nstr,'"'.join(eles)))
            nstr = ''
        else:
            nstr += line
    return '\n'.join(rl)

def retry_decorator(func):
    def wrapper(*args, **kwargs):
        i = 0
        while i < 3:
            try:
                result = func(*args, **kwargs)
                return result
            except:
                i += 1
                time.sleep(1)
    return wrapper

def updateState(val):
    try:
        stateManager = context.stateManager
        stateMap = stateManager.getState(Scope.CLUSTER)
        oldMap = stateMap.toMap()
        if 'conn_num' in oldMap.keys():    
            newMap = {'conn_num' : str(int(oldMap['conn_num']) + val)}
            stateManager.replace(stateMap, newMap, Scope.LOCAL)
        else:
            newMap = {'conn_num' : str(1)}
            stateManager.setState(newMap, Scope.LOCAL)
        LOG.info(context.stateManager.getState(Scope.CLUSTER).toMap())
    except:
        LOG.error(getTracebackStr())
        raise

def getURL(path, component_uid):
    '''
        path :
            flow
            processor
            process-groups
    '''
    url = 'http://localhost:8080/nifi-api/%s/%s' % (path, component_uid)

    return url

def get_pg_list(pg_id):
    '''
        The form of return like
        [
            {
                'pg_id': <process-group id>,
                'pg_name': <process_group name>
            },
            ...
        ]
    '''
    try:
        url = getURL('process-groups', pg_id)
        result_fd = urllib.urlopen(url)
        status_code = result_fd.getcode()
        if status_code == 200:
            result = json.loads(result_fd.read())
            result_fd.close()
            if "parentGroupId" in result["component"].keys():
                return get_pg_list(result["component"]["parentGroupId"]) + [{"pg_id": pg_id, "pg_name": result["component"]["name"]}]
            else:
                return [{"pg_id": pg_id, "pg_name": result["component"]["name"]}]
        else:
            LOG.error(result)
    except Exception as ex:
        LOG.error(getTracebackStr())
        LOG.info("Failed URL : %s" % url)
        raise

def get_processor_info(processor_id):
    '''
        return value: Dict
            <GET result> + <process groups concatenated>
    '''
    try:
        url = getURL('processors', processor_id)
        result_fd = urllib.urlopen(url)
        status_code = result_fd.getcode()
        if status_code == 200:
            result = json.loads(result_fd.read())
            result_fd.close()
            result["extraInfo"] = {}
            result["extraInfo"]["pgs"] = get_pg_list(result["component"]["parentGroupId"])
        else:
            LOG.error(result)
        return result
    except Exception as ex:
        LOG.error(getTracebackStr())
        LOG.info("Failed URL : %s" % url) 
        raise

class WriteCallback(OutputStreamCallback):
    def __init__(self, content=None):
        self.content = content

    def process(self, out):
        out.write(self.content)


class IrisLoader():
    def __init__(self, ip, port, user, pwd, db, field_sep, record_sep, timeout, remove, error_path, direct=False):
        self.conn = False
        self.cursor = False
        self.host = "%s:%s" % (str(ip), str(port))
        self.record_sep = record_sep
        self.load_status = {
            'load_starttime': None,
            'load_endtime': None,
            'load_runtime': None,
            'dat_size': None,
            'record_count': None,
            'success_count': 0,
            'table': None,
            'key': None,
            'partition': None,
            'success_or_fail': 'fail',
            'fail_cause': ''
            }
        self.remove = False
        if remove.lower() in ('true', 't'):
            self.remove = True
        self.error_path = error_path
        try:
            LOG.info('%s %s %s %s %s' % (self.host, user, pwd, str(direct), db))
            self.conn = M6.Connection(self.host, str(user), str(pwd), Direct=direct, Database=str(db))
            self.cursor = self.conn.Cursor()
            self.cursor.SetFieldSep(str(field_sep))
            self.cursor.SetRecordSep(str(record_sep))
            self.cursor.SetTimeout(str(timeout))
            updateState(1)
        except Exception as e:
            LOG.error(getTracebackStr())
            LOG.error(e, exc_info=True)

    def get_status(self):
        return self.load_status

    def isolate_file(self, table, dat_path):
        try:
            isolate_path = os.path.join(self.error_path, table)
            if not os.path.exists(isolate_path):
                os.makedirs(isolate_path)
            errfile_path = os.path.join(isolate_path, os.path.basename(dat_path))
            shutil.copy(dat_path, errfile_path)
            LOG.info("Copy dat-file for error to: %s" % errfile_path)
        except Exception, ex:
            LOG.error(getTracebackStr())
            LOG.error(ex)
            

    def load(self, table, key, partition, ctl_path, dat_path):
        result = True
        self.load_status["table"] = table
        self.load_status["key"] = key
        self.load_status["partition"] = partition
        self.load_status["ctl_path"] = ctl_path
        self.load_status["dat_path"] = dat_path

        time_before_load = dt.datetime.now()
        self.load_status["load_starttime"] = time_before_load.strftime("%Y-%m-%d %H:%M:%S")

        try:
            f = open(dat_path, 'r')
            self.load_status["record_count"] = f.read().count(record_sep)
            f.close()
        except Exception as ex:
            self.load_status["fail_cause"] = getTracebackStr()
            return False

        try:
            if not os.path.exists(dat_path):
                self.load_status["fail_cause"] = 'DAT-File Not Exist : %s' % dat_path
                LOG.info('DAT-File Not Exist : %s' % dat_path)
                self.conn.close()
                updateState(-1)
                return False

            #Iris Load
            LOG.info('%s %s %s %s %s' % (table, key, partition, ctl_path, dat_path))
            strResult = ''

            if self.cursor:
                strResult = self.cursor.Load(table, key, partition, ctl_path, dat_path)
            else:
                self.load_status["fail_cause"] = 'Iris Cursor is pointing null pointer'
                self.isolate_file(table, dat_path)
                LOG.error('Iris Cursor is pointing null pointer')
                self.conn.close()
                updateState(-1)
                return False

            time_after_load = dt.datetime.now()
            self.load_status["load_endtime"] = time_after_load.strftime("%Y-%m-%d %H:%M:%S")
            self.load_status["load_runtime"] = (time_after_load - time_before_load).total_seconds()
            self.load_status["dat_size"] = os.path.getsize(dat_path)

            if "+OK SUCCESS" not in strResult:
                result = False
                self.isolate_file(table, dat_path)
                self.load_status["fail_cause"] = strResult[:1000]
                LOG.error(strResult[:1000])
            else:
                LOG.info(strResult[:1000])
                self.load_status["success_or_fail"] = "success"
                self.load_status["success_count"] = int(strResult[29:])
                if self.remove:
                    os.remove(dat_path)

            self.cursor.Close()
            self.conn.close()
            updateState(-1)

            return result
        except Exception, ex:
            self.load_status["fail_cause"] = getTracebackStr()
            self.isolate_file(table, dat_path)
            LOG.error(getTracebackStr())
            self.cursor.Close()
            self.conn.close()
            updateState(-1)
            return False

originalFlowFile = session.get()
if originalFlowFile != None:
    '''
        -Essential properties which must be listed-
            ip
            port
            user
            pwd
            db
            field_sep
            record_sep
            timeout
            direct
            ctl_path
            process_id
            remove
            error_path
            log_dir
            log_suffix
    '''
    ip = str(ip)
    port = str(port)
    user = str(user)
    pwd = str(pwd)
    db = str(db)
    field_sep = str(field_sep)
    record_sep = str(record_sep)
    timeout = str(timeout)
    remove = str(remove)
    error_path = str(error_path)
    log_dir = str(log_dir)
    log_suffix = str(log_suffix)

    iris_conn['field_sep'] = field_sep
    iris_conn['record_sep'] = record_sep
    iris_conn['remove'] = remove
    iris_conn['error_path'] = error_path

    log_name = '%s-%s.log' % (str(context.name), log_suffix)
    log_path = os.path.join(log_info["log_dir"], log_name)

    if (direct in ('false', 'False')) or ('direct' not in globals()):
        direct = False

    #------------------------------------------------------------------------------------
    if not os.path.exists(os.path.dirname(log_path)):
        os.makedirs(os.path.dirname(log_path))
    LOG = logging.getLogger('')
    formatter = logging.Formatter(log_info["formatter"])

    LOG.setLevel(logging.DEBUG)
    file_Handler = handlers.RotatingFileHandler(log_path, log_info['mode'], log_info['maxBytes'], log_info['backupCount'])
    file_Handler.setFormatter(formatter)
    if not len(LOG.handlers):
        LOG.addHandler(file_Handler)
    #------------------------------------------------------------------------------------

    try:
        # Get attributes
        tablename = originalFlowFile.getAttribute('tablename')
        key = originalFlowFile.getAttribute('key')
        partition = originalFlowFile.getAttribute('partition')
        dat_path = originalFlowFile.getAttribute('dat_path')
        ctl_path = originalFlowFile.getAttribute('ctl_path')

        # Load
        iris_conn['field_sep'] = field_sep
        iris_conn['record_sep'] = record_sep
        iris_conn['remove'] = remove
        iris_conn['error_path'] = error_path

        iris_obj = IrisLoader(**iris_conn)
        result = iris_obj.load(tablename, key, partition, ctl_path, dat_path)

        # Generate content
        info = get_processor_info(process_id)
        info["extraInfo"]["load-status"] = iris_obj.get_status()
        
        # Transfer
        flowFile = session.create(originalFlowFile)
        #flowFile = session.putAttribute(originalFlowFile, 'filename', os.path.basename(dat_path))
        flowFile = session.write(flowFile, WriteCallback(json.dumps(info, indent=4)))
        if result:
            session.transfer(flowFile, REL_SUCCESS)
        else:
            session.transfer(flowFile, REL_FAILURE)
        session.remove(originalFlowFile)
    except Exception, ex:
        LOG.error(getTracebackStr())
        LOG.info(info)
        session.transfer(originalFlowFile, REL_FAILURE)
        session.remove(originalFlowFile)
        raise
