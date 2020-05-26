# coding:utf-8
import os
import sys
import time
import datetime
import re
import xlwt
import pprint

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from collections import OrderedDict as odd

try:
    import configparser as cp
except Exception:
    import ConfigParser as cp

import GetConfig as gc

import logging
logging.basicConfig()

# <<<Get Config Field>>>
setting = gc.Setting()
error_level = setting.message_level()

oddHAAPErrorDict = setting.oddRegularTrace()

# <<<Get Config Field>>>


def deco_OutFromFolder(func):
    strOriFolder = os.getcwd()

    def _deco(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as E:
            # print(func.__name__, E)
            pass
        finally:
            os.chdir(strOriFolder)

    return _deco


def deco_Exception(func):

    def _deco(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as E:
            print(func.__name__, E)

    return _deco


def time_now_folder():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def time_now_to_show():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def is_Warning(intValue, data):
    '''
    data is int or a tuple
    '''
    if isinstance(data, int):
        print('<>')
        if intValue > data:
            return True
    else:
        if intValue >= data[1]:
            return 2
        elif intValue >= data[0]:
            return 1
        else:
            return 0


def is_trace_level(num):
    if num in (1, 2, 3):
        return True


def is_IP(strIP):
    reIP = re.compile(
        '^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if reIP.match(strIP):
        return True
    else:
        return False


def is_IP_list(lstIP):
    return all(map(is_IP, lstIP))


def is_file(strFileName):
    if os.path.isfile(strFileName):
        return True
    else:
        return False

    
def is_folder(strDirName):
    if os.path.isdir(strDirName):
        return True
    else:
        return False


def is_port(intPortNum):
    if type(intPortNum) == int:
        return True
    if type(intPortNum) == str:
        if intPortNum.isdigit():
            if type(eval(intPortNum)) == int:
                return True
    return False


def ShowErr(*argvs):
    '''
    Four argv:
    ClassName, FunctionName, MessageGiven, MessageRaised
    '''
    if error_level == 1:
        print(str('''
----------------------------------------------------------------------------
|*Error message:                                                           |
|    Error message: {:<55}|
|        {:<66}|
----------------------------------------------------------------------------\
'''.format(argvs[2], err_msg=(argvs[3] if argvs[3] else ''))))
    elif error_level == 2:
        pass
    elif error_level == 3:
        print(str('''
----------------------------------------------------------------------------
|*Error message:                                                           |
|    Class name :   {:<55}|
|    Function name: {:<55}|
|    Error message: {:<55}|
|        {:<66}|
----------------------------------------------------------------------------\

'''.format(argvs[0], argvs[1], argvs[2], err_msg=(argvs[3] if argvs[3] else ''))))


def GotoFolder(strFolder):

    def _mkdir():
        if strFolder:
            if os.path.exists(strFolder):
                return True
            else:
                try:
                    os.makedirs(strFolder)
                    return True
                except Exception as E:
                    print('Create folder "{}" fail with error:\n\t"{}"'.format(
                        strFolder, E))

    if _mkdir():
        try:
            os.chdir(strFolder)
            return True
        except Exception as E:
            print('Change to folder "{}" fail with error:\n\t"{}"'.format(
                strFolder, E))


class Timing(object):

    def __init__(self):
        self.scdl = BlockingScheduler()

    def add_interval(self, job, intSec):
        trigger = IntervalTrigger(seconds=intSec)
        self.scdl.add_job(job, trigger)
    
    def add_cycle(self, job, args):
        cycle = args[0]
        day = args[1]
        hours = args[2]
        minutes = args[3]
        if cycle == 'week':
            trigger = CronTrigger(day_of_week=day, hour=hours, minute=minutes)
            self.scdl.add_job(job, trigger)
        elif cycle == 'day':
            trigger = CronTrigger(hour=hours, minute=minutes)
            self.scdl.add_job(job, trigger)
    
    def add_once(self, job, rdate):
        try:
            self.scdl.add_job(job, 'date', run_date=rdate, max_instances=6)
        except ValueError as E:
            self.scdl.add_job(job, 'date')
        
    def stt(self):
        self.scdl.start()

    def stp(self):
        self.scdl.shutdown()


class TimeNow(object):

    def __init__(self):
        self._now = time.localtime()

    def y(self):  # Year
        return (self._now[0])

    def mo(self):  # Month
        return (self._now[1])

    def d(self):  # Day
        return (self._now[2])

    def h(self):  # Hour
        return (self._now[3])

    def mi(self):  # Minute
        return (self._now[4])

    def s(self):  # Second
        return (self._now[5])

    def wd(self):  # Day of the Week
        return (self._now[6])

class TraceAnalyse():
    def __init__(self, strTraceFolder):
        self.target = strTraceFolder
        self.regular_dict = oddHAAPErrorDict

    def _get_trace_file_list(self):
        lstTraceFile = []
        lstFile = os.listdir('.')
        for strFileName in lstFile:
            if (lambda i: i.startswith('Trace_'))(strFileName):
                lstTraceFile.append(strFileName)
        return lstTraceFile

    def _read_file(slef, strFileName):
        try:
            with open(strFileName, 'r+') as f:
                strTrace = f.read()
            return strTrace.strip().replace('\ufeff', '')
        except Exception as E:
            print('Open file "{}" failed with error:\n\t"{}"'.format(
                strFileName, E)) 

    def _write_to_excel(self, objExcel,error_type,tpl_error):
        objSheet = objExcel.add_sheet(error_type)
        for x in range(len(tpl_error)):
            for y in range(len(tpl_error[x])):
                objSheet.write(
                    x, y, tpl_error[x][y].strip().replace(
                        "\n", '', 1))

    def _find_error(self, strFileName):
        strTrace = self._read_file(strFileName)
        objExcel = xlwt.Workbook()
        save_flag = 0
        for error_type in self.regular_dict.keys():
            re_error = re.compile(eval(self.regular_dict[error_type]))
            tpl_error = re_error.findall(strTrace)
            if len(tpl_error) > 0:
                print('*** %-3.d times of %-12s found...' % (len(tpl_error)+1,error_type))
                self._write_to_excel(objExcel,error_type,tpl_error)
                save_flag += 1
        if save_flag:
            objExcel.save('TraceAnalyze_%s' % strFileName.replace('.log','.xls'))
        else:
            print('--- No error found in "%s"' % strFileName)

    def _analyse_file(self):
        lstTraceFiles = self._get_trace_file_list()
        for trace_file in lstTraceFiles:
            print('\nStart to analysing %s ...' % trace_file)
            self._find_error(trace_file)
            
    def run(self):
        strOriginalFolder = os.getcwd()
        try:
            GotoFolder(self.target)
            self._analyse_file()
        finally:
            os.chdir(strOriginalFolder)



if __name__ == '__main__':
    pass

