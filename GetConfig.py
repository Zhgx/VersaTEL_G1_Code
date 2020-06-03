# coding:utf-8

from collections import OrderedDict as Odd
try:
    import configparser as cp
except Exception:
    import ConfigParser as cp

name_of_config_file = 'config.ini'
name_of_sys_config_file = 'sys_cfg.ini'


def read_config_file():
    objCFG = cp.ConfigParser(allow_no_value=True)
    objCFG.read(name_of_config_file)
    return objCFG

def read_sys_config_file():
    objCFG = cp.ConfigParser(allow_no_value=True)
    objCFG.read(name_of_sys_config_file)
    return objCFG

class EngineConfig(object):
    """docstring for EngineConfig"""

    def __init__(self):
        #        super(EngineConfig, self).__init__()
        self.cfg = read_config_file()
        self.sys_cfg = read_sys_config_file()
        self.oddEngines = self._odd_engines()

    def _odd_engines(self):
        oddEngines = Odd()
        for engine in self.cfg.items('Engines'):
            oddEngines[engine[0]] = engine[1]
        return oddEngines

    def list_engines_alias(self):
        return self.oddEngines.keys()

    def list_engines_IP(self):
        return self.oddEngines.values()

    def telnet_port(self):
        return self.cfg.getint('EngineSetting', 'telnet_port')

    def FTP_port(self):
        return self.cfg.getint('EngineSetting', 'ftp_port')

    def password(self):
        return str(self.cfg.get('EngineSetting', 'password'))

    def trace_level(self):
        return self.cfg.getint('EngineSetting', 'trace_level')


class DBConfig(object):
    """docstring for DBConfig"""

    def __init__(self):
        # super(DBConfig, self).__init__()
        self.cfg = read_config_file()
        self.sys_cfg = read_sys_config_file()

    def host(self):
        return self.sys_cfg.get('DBSetting', 'host')

    def port(self):
        return self.sys_cfg.getint('DBSetting', 'port')

    def name(self):
        return  self.sys_cfg.get('DBSetting', 'name')


class SwitchConfig(object):
    """docstring for SwitchConfig"""

    def __init__(self):
        self.cfg = read_config_file()
        self.oddSWAlias = self._odd_switches_Alias()
        self.oddSWPort = self._odd_switches_Ports()

    def _odd_switches_Alias(self):
        oddSWAlias = Odd()
        for sw in self.cfg.items('SANSwitches'):
            oddSWAlias[sw[0]] = sw[1]
        return oddSWAlias

    def _odd_switches_Ports(self):
        oddSWPort = Odd()
        for sw in self.cfg.items('SANSwitchePorts'):
            oddSWPort[sw[0]] = eval(sw[1])
        return oddSWPort
   
    def list_switch_alias(self):
        return self.oddSWAlias.keys()

    def list_switch_IP(self):
        return self.oddSWAlias.values()

    def list_switch_ports(self):
        return self.oddSWPort.values()

    def SSH_port(self):
        return self.cfg.getint('SANSwitcheSetting', 'ssh_port')

    def username(self):
        return str(self.cfg.get('SANSwitcheSetting', 'username'))

    def password(self):
        return str(self.cfg.get('SANSwitcheSetting', 'password'))

    def sw_enable_status(self):
        return self.cfg.get('SANSwitcheSetting', 'enable')

    def threshold_total(self):
        lstThreshold = []
        # level1 = self.cfg.getint('Threshold', 'SWTotal_increase_Notify')
        level2 = self.cfg.getint('Threshold', 'SWTotal_increase_Warning')
        level3 = self.cfg.getint('Threshold', 'SWTotal_increase_Alarm')
        # lstThreshold.append(level1)
        lstThreshold.append(level2)
        lstThreshold.append(level3)
        return tuple(lstThreshold)


class EmailConfig(object):
    """docstring for EmailConfig"""

    def __init__(self):
        self.cfg = read_config_file()

    def email_host(self):
        return str(self.cfg.get('EmailSetting', 'host'))

    def email_port(self):
        return self.cfg.getint('EmailSetting', 'port')

    def email_password(self):
        return str(self.cfg.get('EmailSetting', 'password'))

    def email_sender(self):
        return str(self.cfg.get('EmailSetting', 'sender'))

    def email_receiver(self):
        return str(self.cfg.get('EmailSetting', 'receiver'))

    # Whether to Turn off Mail Function
    def email_enable(self):
        return self.cfg.get('EmailSetting', 'enable')

    def email_encrypt(self):
        return self.cfg.get('EmailSetting', 'encrypt')


class Setting(object):
    """docstring for Setting"""

    def __init__(self):
        self.cfg = read_config_file()
        self.sys_cfg = read_sys_config_file()

    def message_level(self):
# Get the time interval Settings
        return int(self.sys_cfg.get('MessageLogging', 'msglevel'))

    def interval_web_refresh(self):
        return self.cfg.getint('Interval', 'web_refresh')

    def interval_haap_update(self):
        return self.cfg.getint('Interval', 'haap_update')

    def interval_sansw_update(self):
        return self.cfg.getint('Interval', 'sansw_update')

    def interval_warning_check(self):
        return self.cfg.getint('Interval', 'warning_check')
# Get mail cycle Settings

    def cron_cycle(self):
        return self.cfg.get('Cycle', 'cycle')

    def cron_day(self):
        return self.cfg.getint('Cycle', 'day')

    def cron_hour(self):
        return self.cfg.getint('Cycle', 'hour')

    def cron_minutes(self):
        return self.cfg.getint('Cycle', 'minutes')

    def folder_collection(self):
        return  self.sys_cfg.get('FolderSetting', 'collection')

    def folder_swporterr(self):
        return  self.sys_cfg.get('FolderSetting', 'swporterr')

    def folder_trace(self):
        return  self.sys_cfg.get('FolderSetting', 'trace')

    def folder_traceanalyse(self):
        return  self.sys_cfg.get('FolderSetting', 'traceanalyse')

    def folder_cfgbackup(self):
        return  self.sys_cfg.get('FolderSetting', 'cfgbackup')

    def folder_PeriodicCheck(self):
        return  self.sys_cfg.get('FolderSetting', 'PeriodicCheck')
   
    def PCEngineCommand(self):
        return list(i[0] for i in self.sys_cfg.items('PCEngineCommand'))

    def PCSANSwitchCommand(self):
        return list(i[0] for i in self.sys_cfg.items('PCSANSwitchCommand'))

    def oddRegularTrace(self):
        oddRegularTrace = Odd()
        for i in self.sys_cfg.items('TraceRegular'):
            oddRegularTrace[i[0]] = i[1]
        return oddRegularTrace


class General(object):
    """docstring for General"""

    def __init__(self):
        self.cfg = read_config_file()

    def get_PRODUCT(self):
        return str(self.cfg.get('General', 'PRODUCT'))


if __name__ == '__main__':
    print(Setting().folder_collection())
    pass
