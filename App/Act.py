# 1.1.1

import sys

import time
import os
import shutil
import re
import datetime
import win32evtlog
import win32evtlogutil
import win32con
import winerror
from datetime import date
sys.path.append("C:\\MOBILE\\Local\\CMS")
from App.Config import Config as Conf
from App import API, Log, Database, File
from App import Resource as Res

LOG = Log.Log_Manager()


global o_nova
global o_sys
global o_file
global o_crMsg
global o_tbl
global o_DBPrep


class Init:

    def __init__(self):
        global o_nova
        global o_sys
        global o_file
        global o_crMsg
        global o_tbl
        global o_DBPrep

        o_nova = API.Nova()
        o_sys = API.System()
        o_file = File.NovaBin()
        o_crMsg = Res.CreateMessage()
        o_tbl = Database.Tables()
        o_DBPrep = Database.Prepare()


class Process(Init):
    @staticmethod
    def start(data):
        if data == Res.ProcList[0]:
            o_nova.RunNova()

    @staticmethod
    def terminate(data):
        if data == Res.ProcList[1]:
            o_nova.TerminateMars()
        if data == Res.ProcList[0]:
            o_nova.TerminateNova()

    @staticmethod
    def restart(data):
        if data == Res.ProcList[0]:
            o_nova.RestartNova()


class System(Init):
    @staticmethod
    def preshutdown():
        o_file.BackupHandle()

    def rebootinit(self):
        self.preshutdown()
        time.sleep(30)
        o_sys.RestartPC()


class Files(Init):

    # Archives logs
    @staticmethod
    def logarch():
        arch_name = None
        list_for_archiving = []
        # Lists files stored in a directory
        for file in os.listdir(Conf.logPath):
            # Continues to work only with files with the .log extension
            if re.search('log', file):
                # Checks the creation date of log files
                log_date = datetime.datetime.strptime(re.findall(r'\d{4}-\d{2}-\d{2}', file)[0], "%Y-%m-%d")
                if log_date.date() < date.today():
                    arch_name = str(log_date.date())
                    LOG.CMSLogger('Marked for archiving ' + file)
                    list_for_archiving.append(file)
        # Checks if the folder that I'm going to create exists
        if list_for_archiving and not os.path.exists(Conf.logPath + str(date.today())):
            os.mkdir(Conf.logPath + arch_name)
            # Move logs to folder
            for file in list_for_archiving:
                shutil.move(Conf.logPath + file, Conf.logPath + arch_name + '\\' + file)
                LOG.CMSLogger('Moved to archive ' + file)
            # Archives a folder
            shutil.make_archive(base_name=Conf.logPath + arch_name, format='zip', root_dir=Conf.logPath + arch_name, )
            shutil.rmtree(Conf.logPath + arch_name)
        else:
            LOG.CMSLogger('No logs found to archive')

    # Removes obsolete logs
    @staticmethod
    def logdel():
        list_for_deleting = []

        # Lists files stored in a directory
        for file in os.listdir(Conf.logPath):
            # Continues to work only with files with the .zip extension
            if re.search('zip', file):
                # Checks the date the archive was created
                if (datetime.datetime.strptime(re.findall(r'\d{4}-\d{2}-\d{2}', file)[0],
                                               "%Y-%m-%d").date() - date.today()).days < -90:
                    list_for_deleting.append(file)

        # Removes obsolete archives
        for file in list_for_deleting:
            os.remove(Conf.logPath + file)
            LOG.CMSLogger('File deleted ' + file)


class SysInit(Files):

    def initcms(self, q_internal):
        data = self.check_self()
        self.put_sys_run(q_internal)
        self.logarch()
        self.logdel()
        self.check_lastselfinitstd(q_internal)
        if data:
            self.CheckLastStd(q_internal)
        else:
            pass

    @staticmethod
    def check_db():
        data = True
        if os.path.exists(Conf.DBFolder):
            if os.path.exists(Conf.DBPath):
                LOG.CMSLogger('Database file exist')
            else:
                handle = Database.DBFoo()
                handle.CreateTables()
                data = False
                LOG.CMSLogger('Database file created')
        else:
            os.mkdir(Conf.DBFolder)
            handle = Database.DBFoo()
            handle.CreateTables()
            data = False
            LOG.CMSLogger('Database file created')
        return data

    def check_self(self):
        data = self.check_db()
        return data

    @staticmethod
    def put_sys_run(q_internal):

        q_internal.put(o_DBPrep.SystemRunPrep(datetime.datetime.now()))

    @staticmethod
    def check_lastselfinitstd(q_internal):

        try:
            last_std = o_tbl.SelfInitShutdown().select().order_by(o_tbl.SelfInitShutdown.id.desc()).get()
        except:
            last_std = None
        if last_std:
            count = o_tbl.SelfInitShutdown().select().where(
                (o_tbl.SelfInitShutdown.datetime.year == datetime.date.today().year) &
                (o_tbl.SelfInitShutdown.datetime.month == datetime.date.today().month) &
                (o_tbl.SelfInitShutdown.datetime.day == datetime.date.today().day)).count()
            if last_std.datetime.date() == datetime.datetime.now().date():
                if (datetime.datetime.now() - last_std.datetime).seconds <= 600:
                    if count >= 2:
                        q_internal.put(o_crMsg.SetFlagUAV_0())
                        q_internal.put(o_crMsg.SetFlagCont_0())

                        msg = 'Exceeded quantity ' \
                                'Attempts to restart the system: {} ' \
                                'Last reboot: {} '.format(count, last_std.datetime)

                        q_internal.put(o_crMsg.SendMail(msg))
                        LOG.CMSLogger(msg)
                        LOG.CMSLogger('Restart prohibited ')
                    else:
                        q_internal.put(o_crMsg.SetFlagUAV_1())
                        q_internal.put(o_crMsg.SetFlagCont_1())

                        msg = 'The frequency of attempts to ' \
                              'restart the system has been exceeded ' \
                                        'Last reboot: {} '.format(last_std.datetime)

                        LOG.CMSLogger(msg)
                elif count >= 5:
                    q_internal.put(o_crMsg.SetFlagUAV_1())
                    q_internal.put(o_crMsg.SetFlagCont_1())

                    msg = 'The frequency of attempts to ' \
                          'restart the system has been exceeded ' \
                          'Last reboot: {} '.format(last_std.datetime)

                    q_internal.put(o_crMsg.SendMail(msg))
                    LOG.CMSLogger(msg)

                    LOG.CMSLogger('Restart prohibited')
                else:
                    q_internal.put(o_crMsg.SetFlagUAV_2())
                    q_internal.put(o_crMsg.SetFlagCont_2())

                    LOG.CMSLogger('Restart allowed')
            else:
                q_internal.put(o_crMsg.SetFlagUAV_2())
                q_internal.put(o_crMsg.SetFlagCont_2())

                LOG.CMSLogger('Restart allowed')
        else:
            q_internal.put(o_crMsg.SetFlagUAV_2())
            q_internal.put(o_crMsg.SetFlagCont_2())

            LOG.CMSLogger('No data on system reboots')
            LOG.CMSLogger('Restart allowed')

    def CheckLastStd(self, q_Internal):
        lastStd = None

        machine = None
        ev = True
        br = False

        preCurrentRun = None

        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        evTypes = {win32con.EVENTLOG_INFORMATION_TYPE: 'EVENTLOG_INFORMATION_TYPE',
                    win32con.EVENTLOG_WARNING_TYPE: 'EVENTLOG_WARNING_TYPE',
                    win32con.EVENTLOG_ERROR_TYPE: 'EVENTLOG_ERROR_TYPE'}
        logType = 'System'
        handle = win32evtlog.OpenEventLog(machine, logType)
        evSource = ['User32', 'Microsoft-Windows-Winlogon', 'Microsoft-Windows-Kernel-Power',
                  'Microsoft-Windows-Kernel-Boot',
                  'EventLog', 'Kernel-Boot']

        time.sleep(10)
        currentRun = o_tbl.SystemRun().select().order_by(o_tbl.SystemRun.id.desc()).get()
        if o_tbl.SystemRun().select().count() == 1:
            LOG.CMSLogger('CMS запущена впервые на этекущей системе')
            exit()
        else:
            preCurrentRun = o_tbl.SystemRun().select().where(o_tbl.SystemRun.id == currentRun.id - 1).get()

        if o_tbl.SelfInitShutdown().select().count() == 0:
            LOG.CMSLogger('CMS еще не отключал текущую систему')
            exit()
        else:
            lastStd = o_tbl.SelfInitShutdown().select().where(
                o_tbl.SelfInitShutdown.key == ('reboot' or 'shutdown')).order_by(o_tbl.SelfInitShutdown.id.desc()).get()

        timeLine = (datetime.datetime.now() - preCurrentRun.datetime).seconds

        if lastStd.id != preCurrentRun.id:
            msgTxt = 'Предыдущее отключение не было инициировано CMS, либо произошел сбой записи в БД \n'
            while ev:
                try:
                    ev = win32evtlog.ReadEventLog(handle, flags, 0)
                    for ev_obj in ev:
                        the_time = ev_obj.TimeGenerated

                        if (datetime.datetime.now() - the_time).seconds <= timeLine:
                            if str(ev_obj.SourceName) in evSource:
                                src = str(ev_obj.SourceName)
                                ev_type = str(evTypes[ev_obj.EventType])
                                msg = str(win32evtlogutil.SafeFormatMessage(ev_obj, logType))
                                ev_id = str(winerror.HRESULT_CODE(ev_obj.EventID))

                                if src == 'User32' and ev_id == '1074':
                                    if re.findall(r'RuntimeBroker.exe', msg):
                                        if re.findall(r'Перезапустить', msg):
                                            msgTxt += 'Система была перезагружена пользователем, \n' \
                                                        'Время: {}, \n' \
                                                        'Тип: {}, \n' \
                                                        'Источник: {}, \n' \
                                                        'Код события: {}, \n' \
                                                        'Описание: {} '.format(the_time.Format(), ev_type, src, ev_id, msg)
                                            br = True

                                        elif re.findall(r'Выключение питания', msg):
                                            msgTxt += 'Система была выключена пользователем, ' \
                                                      'Время: {}, \n' \
                                                      'Тип: {}, \n' \
                                                      'Источник: {}, \n' \
                                                      'Код события: {}, \n' \
                                                      'Описание: {} '.format(the_time.Format(), ev_type, src, ev_id,
                                                                             msg)
                                            br = True
                        if br:
                            break
                    if br:
                        break
                except:
                   pass
            if msgTxt:
                LOG.CMSLogger(msgTxt)
                q_Internal.put(o_crMsg.SendMail(msgTxt))
            win32evtlog.CloseEventLog(handle)
