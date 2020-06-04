# coding:utf-8
from __future__ import print_function
import time
import sys
from flask import Flask, render_template, request
from gevent.pywsgi import WSGIServer
from threading import Thread
import time
import operator
import datetime
import SANSW as sw
import HAAP as haap
import Sundry as s
import SendEmail as se
import DB as db
import GetConfig as gc
try:
    import configparser as cp
except Exception:
    import ConfigParser as cp

# <<<Get Config Field>>>
setting = gc.Setting()
interval_web_refresh = setting.interval_web_refresh()
interval_haap_update = setting.interval_haap_update()
interval_sansw_update = setting.interval_sansw_update()
interval_warning_check = setting.interval_warning_check()

cron_cycle = setting.cron_cycle()
cron_day = setting.cron_day()
cron_hour = setting.cron_hour()
cron_minutes = setting.cron_minutes()
cycle_msg_args = [cron_cycle, cron_day, cron_hour, cron_minutes]

swcfg = gc.SwitchConfig()
tuplThresholdTotal = swcfg.threshold_total()
lst_sansw_IP = swcfg.list_switch_IP()
lst_sansw_alias = swcfg.list_switch_alias()
sw_enable_status = swcfg.sw_enable_status()

haapcfg = gc.EngineConfig()
oddEngines = haapcfg._odd_engines()
trace_level_cfg = haapcfg.trace_level()
lst_haap_IP = oddEngines.values()
lst_haap_alias = oddEngines.keys()
# <<<Get Config Field>>>

# <<web show table title>>
lstDescHAAP = ('Engine', 'IP', 'Status', 'Uptime',
               'Master', 'Cluster', 'Mirror', 'Get Trace')
lstDescSANSW = ('Switch', 'IP', 'Encout', 'DiscC3',
                'LinkFail', 'LossSigle', 'LossSync', 'Total')
lstWarning = ('Time', 'Level', 'Device', 'IP', 'Message')


def monitor_rt_1_thread():
    t1 = Thread(target=start_web, args=('rt',))
    t1.setDaemon(True)
    t1.start()
    try:
        while t1.isAlive():
            pass
    except KeyboardInterrupt:
        stopping_web(3)


def monitor_db_4_thread():
    target = [start_web, haap_interval_check, sansw_interval_check,
              warning_interval_check, Monitoring_heart_check]
    args = [('db',), (interval_haap_update,), (interval_sansw_update,),
            (interval_warning_check,), (cycle_msg_args,)]
    thread = []
    for target, args in zip(target, args):
        t = Thread(target=target, args=args)
        t.setDaemon(True)
        t.start()
        thread.append(t)

    while True:
        for thread_value in thread:
            try:
                while thread_value.isAlive():
                    break
            except KeyboardInterrupt:
                stopping_web(3)
                sys.exit()


def start_web(mode):
    '''
tlu = Time Last Update
    '''

    app = Flask(__name__)

    @app.route("/", methods=['GET', 'POST'])
    def home():
        if request.args.get('trace'):
            TRACE = request.args.get('trace')
            haap.get_trace(TRACE, trace_level_cfg)
        else:
            pass

        if mode == 'rt':
            StatusHAAP = haap_rt_info_to_show()
            StatusSANSW = sansw_rt_info_to_show()
            if StatusHAAP:
                StatusHAAP.sort(key=operator.itemgetter(0))
                tlu_haap = s.time_now_to_show()
                status_warning = 0
            else:
                tlu_haap = s.time_now_to_show()
                status_warning = 0

            if StatusSANSW:
                StatusSANSW.sort(key=operator.itemgetter(0))
                tlu_sansw = s.time_now_to_show()
                status_warning = 0
            else:
                tlu_sansw = s.time_now_to_show()
                status_warning = 0

        elif mode == 'db':
            lstWarningList = db.get_unconfirm_warning()
            if request.method == 'GET' and lstWarningList:
                error = 1
            else:
                db.update_warning()
                error = 0

            engine = haap_info_to_show()
            sansw = sansw_info_to_show()
            status_warning = db.get_unconfirm_warning()
            if engine:
                tlu_haap = engine[0]
                StatusHAAP = engine[1]
                StatusHAAP.sort(key=operator.itemgetter(0))

            else:
                tlu_haap = s.time_now_to_show()
                StatusHAAP = [0]

            if sansw:
                tlu_sansw = sansw[0]
                StatusSANSW = sansw[1]
                StatusSANSW.sort(key=operator.itemgetter(0))
            else:
                tlu_sansw = s.time_now_to_show()
                StatusSANSW = [0]

        return render_template("monitor.html",
                               Title_HAAP=lstDescHAAP,
                               Title_SANSW=lstDescSANSW,
                               tlu_haap=tlu_haap,
                               tlu_sansw=tlu_sansw,
                               status_haap=StatusHAAP,
                               status_sansw=StatusSANSW,
                               status_warning=status_warning,
                               interval_web_refresh=interval_web_refresh,
                               sw_enable_status=sw_enable_status
                               )

    @app.route("/warning/")
    def warning():
        lstWarningList = db.get_unconfirm_warning()
        return render_template("warning.html", lstWarningList=lstWarningList,
                               )

    @app.route("/send_email", methods=['GET', 'POST'])
    def send_emails():
        if request.args.get('ey'):
            ey = request.args.get('ey')
            se.send_test()
            meg = "success"
            return meg
        else:
            pass

    # FLASK_APP = myapp.py
    # FLASK_ENV = development
    WSGIServer(('0.0.0.0', 5000), app).serve_forever()
    # FLASK_ENV=development
    # app.run(debug=False, use_reloader=False, host='127.0.0.1', port=5000)


def stopping_web(intSec):
    try:
        print('\nStopping web server ', end='')
        for i in range(intSec):
            time.sleep(1)
            print('.', end='')
        time.sleep(1)
        print('\n\nWeb server stopped.')
    except KeyboardInterrupt:
        print('\n\nWeb server stopped.')


def haap_interval_check(intInterval):
    t = s.Timing()
    t.add_interval(check_all_haap, intInterval)
    t.stt()


def sansw_interval_check(intInterval):
    if sw_enable_status == 'yes':
        t = s.Timing()
        t.add_interval(check_all_sansw, intInterval)
        t.stt()
    else:
        return


def warning_interval_check(intInterval):
    t = s.Timing()
    t.add_interval(warning_check, intInterval)
    t.stt()


def Monitoring_heart_check(cycle_msg_args):
    t = s.Timing()
    t.add_cycle(se.send_live, cycle_msg_args)
    t.stt()


def check_all_haap():
    Origin_from_engine, Info_from_engine = haap.data_for_db()
    try:
        Info_from_DB = db.haap_last_record()
        if Info_from_DB:
            for engine in lst_haap_alias:
                lstRT = haap_info_for_judge(Info_from_engine)[engine]
                lstDB = haap_info_for_judge(Info_from_DB.info)[engine]
                haap_judge(lstRT, lstDB, engine).all_judge()
    finally:
        db.haap_insert(datetime.datetime.now(),
                       Origin_from_engine, Info_from_engine)


def check_all_sansw():
    dicAll = sw.get_info_for_DB()
    try:
        if dicAll:
            for sw_alias in lst_sansw_alias:
                int_total_DB = get_switch_total_db(sw_alias)
                dic_sum_total = dicAll[1]
                dic_sum_total = dic_sum_total[sw_alias]
                int_total_RT = dic_sum_total['PE_Total']
                strIP = dic_sum_total['IP']
                sansw_judge(int_total_RT, int_total_DB, strIP, sw_alias)
    finally:
        db.switch_insert(datetime.datetime.now(),
                         dicAll[0], dicAll[1], dicAll[2])


def warning_check():
    unconfirm_warning = db.get_unconfirm_warning()
    if unconfirm_warning:
        se.send_warnmail(unconfirm_warning)
    else:
        print('No unconfirm warning found...')

# check status interval


class haap_judge(object):
    """docstring for haap_judge"""

    def __init__(self, statusRT, statusDB, haap_Alias):
        self.alias = haap_Alias
        self.host = statusRT[0]
        self.statusRT = statusRT
        self.statusDB = statusDB
        self.strTimeNow = s.time_now_to_show()
        self.lstWarningToSend = []

    def judge_AH(self, AHstatus_rt, AHstatus_db):
        str_engine_AH = 'Engine AH'
        if AHstatus_rt == '--':
            return True
        elif AHstatus_rt != 'OK':
            if AHstatus_rt != AHstatus_db:
                db.insert_warning(self.strTimeNow, self.host,
                                  'engine', 2, str_engine_AH, 0)
                self.lstWarningToSend.append([self.strTimeNow, self.host,
                                              self.alias, 2, str_engine_AH])
            return True

    def judge_reboot(self, uptime_second_rt, uptime_second_db):
        str_engine_restart = 'Engine reboot %d secends ago'
        if uptime_second_rt == None or uptime_second_rt == 0:
            return True
        elif uptime_second_rt < uptime_second_db:
            db.insert_warning(self.strTimeNow, self.host,
                              'engine', 2, str_engine_restart % (uptime_second_rt), 0)
            self.lstWarningToSend.append([self.strTimeNow, self.host,
                                          self.alias, 2, str_engine_restart % (uptime_second_rt)])

    def judge_Status(self, Status_rt, Status_db):
        str_engine_status = 'Engine offline'
        if Status_rt != 'OK':
            if Status_rt != Status_db:
                db.insert_warning(self.strTimeNow, self.host,
                                  'engine', 2, str_engine_status, 0)
                self.lstWarningToSend.append([self.strTimeNow, self.host,
                                              self.alias, 2, str_engine_status])

    def judge_Mirror(self, MirrorStatus_rt, MirrorStatus_db):
        str_engine_mirror = 'Engine mirror not ok'
        if MirrorStatus_rt != 'OK' and MirrorStatus_rt != 'No Mirror':
            if MirrorStatus_rt != MirrorStatus_db:
                db.insert_warning(self.strTimeNow, self.host,
                                  'engine', 2, str_engine_mirror, 0)
                self.lstWarningToSend.append([self.strTimeNow, self.host,
                                              self.alias, 2, str_engine_mirror])

    def all_judge(self):
        # try:
        #     if self.statusDB:
        #         if self.judge_AH(self.statusRT[1], self.statusDB[1]):
        #             self.judge_reboot(self.statusRT[2], self.statusDB[2])
        #             self.judge_Status(self.statusRT[3], self.statusDB[3])
        #             self.judge_Mirror(self.statusRT[4], self.statusDB[4])
        # except:
        #     raise('error')
        # finally:
        #     if self.lstWarningToSend:
        #         se.send_warnmail(self.lstWarningToSend)

        if self.statusDB:
            if self.judge_AH(self.statusRT[1], self.statusDB[1]):
                pass
            else:
                self.judge_reboot(self.statusRT[2], self.statusDB[2])
                self.judge_Status(self.statusRT[3], self.statusDB[3])
                self.judge_Mirror(self.statusRT[4], self.statusDB[4])

        if self.lstWarningToSend:
            se.send_warnmail(self.lstWarningToSend)


def sansw_judge(total_RT, total_DB, sansw_IP, sansw_Alias):
    strTimeNow = s.time_now_to_show()
    if (total_DB != None) and (total_RT != None):
        intErrorIncrease = total_RT - total_DB
        intWarninglevel = s.is_Warning(intErrorIncrease, tuplThresholdTotal)
        if intWarninglevel:
            msg = warning_message_sansw(intWarninglevel)
            db.insert_warning(strTimeNow, sansw_IP, 'switch',
                              intWarninglevel, msg, 0)
            se.send_warnmail([[strTimeNow, sansw_IP,
                               sansw_Alias, intWarninglevel, msg]])


def warning_message_sansw(intWarninglevel):
    # if intWarninglevel == 0:
    #     strLevel = 'Notify'
    if intWarninglevel == 1:
        strLevel = 'Warning'
    elif intWarninglevel == 2:
        strLevel = 'Alarm'
    return 'Total error count increase reach level %s' % strLevel


def haap_info_to_show():
    """
    @note: HAAP网页展示数据(时间，status)
    """
    dicALL = db.haap_last_record()
    lstHAAPToShow = []
    if dicALL:
        strTime = dicALL.time.strftime('%Y-%m-%d %H:%M:%S')
        info = dicALL.info
        for engine_alias in info.keys():
            info_status = info[engine_alias]['status']
            info_status.insert(0, engine_alias)
            info_status.append(info[engine_alias]['level'])
            lstHAAPToShow.append(info_status)
        return strTime, lstHAAPToShow


def sansw_info_to_show():
    """
    @note: 获取数据库SANSW要展示的内容（时间，status）
    """
    lst_switch = db.switch_last_info()
    lst_sansw_to_show = []
    if lst_switch:
        strTime = lst_switch.time.strftime('%Y-%m-%d %H:%M:%S')
        switch_total = lst_switch.sum_total
        for sansw_alias in switch_total.keys():
            ip = switch_total[sansw_alias]["IP"]
            PE_sum = switch_total[sansw_alias]["PE_Sum"]
            if PE_sum == None:
                PE_sum = ['--', '--', '--', '--', '--']
            PE_total = switch_total[sansw_alias]["PE_Total"]
            if PE_total == None:
                PE_total = '--'
            warning_level = s.is_Warning(PE_total, tuplThresholdTotal)
            PE_sum.insert(0, ip)
            PE_sum.append(PE_total)
            PE_sum.insert(0, sansw_alias)
            PE_sum.append(warning_level)
            lst_sansw_to_show.append(PE_sum)
        return strTime, lst_sansw_to_show


def haap_info_for_judge(lstInfo):
    """
    @note: 获取数据库具体up_sec
    """
    dicInfo = {}
    if lstInfo:
        list_haap_alias = lstInfo.keys()
        for haap in list_haap_alias:
            list_status = lstInfo[haap]["status"]
            new_list_status_judge = list_status[:]
            list_status_judge = [new_list_status_judge[i]
                                 for i in [0, 1, 2, 4, 5]]
            list_status_judge[2] = lstInfo[haap]['up_sec']
            dicInfo[haap] = list_status_judge
        return dicInfo


def get_switch_total_db(list_switch_alias):
    """
    @note: 获取数据库的Total
    """
    dicALL = db.switch_last_info()
    if dicALL:
        dicALL = dicALL.sum_total
        db_total = dicALL[list_switch_alias]["PE_Total"]
        return db_total


def sansw_rt_info_to_show():
    """
    @note: SANSW要展示的即时内容（status）
    """
    switch_total = sw.get_info_for_DB()[1]
    lst_sansw_to_show = []
    if switch_total:
        for sansw_alias in switch_total.keys():
            ip = switch_total[sansw_alias]["IP"]
            PE_sum = switch_total[sansw_alias]["PE_Sum"]
            if PE_sum == None:
                PE_sum = []
            PE_total = switch_total[sansw_alias]["PE_Total"]
            warning_level = s.is_Warning(PE_total, tuplThresholdTotal)
            PE_sum.insert(0, ip)
            PE_sum.append(PE_total)
            PE_sum.insert(0, sansw_alias)
            PE_sum.append(warning_level)
            lst_sansw_to_show.append(PE_sum)
        return lst_sansw_to_show


def haap_rt_info_to_show():
    """
    @note: HAAP网页展示即时数据(status)
    """
    dicALL = haap.data_for_db()[1]
    lstHAAPToShow = []
    if dicALL:
        for engine_alias in dicALL.keys():
            info_status = dicALL[engine_alias]['status']
            info_status.insert(0, engine_alias)
            info_status.append(dicALL[engine_alias]['level'])
            lstHAAPToShow.append(info_status)
        return lstHAAPToShow


if __name__ == '__main__':
    pass
