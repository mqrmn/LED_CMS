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
from App.Config import Config
from App import API, Log, Database, File
from App import Resource as R

LOG = Log.Log_Manager()

class Init:
    def __init__(self):
        global C_Nova
        global C_Win
        global C_Sys
        global C_File
        C_Nova = API.Nova()
        C_Win = API.Process()
        C_Sys = API.System()
        C_File = File.NovaBin()

class Process(Init):

    def Start(self, data):
        if data == R.ProcList[0]:
            C_Nova.RunNova()

    def Terminate(self, data):
        if data == R.ProcList[1]:
            C_Nova.TerminateMars()
        if data == R.ProcList[0]:
            C_Nova.TerminateNova()

    def Restart(self, data):
        if data == R.ProcList[0]:
            C_Nova.RestartNova()

class System(Init):

    def PreShutdown(self):
        C_File.BackupHandle()

    def RebootInit(self):
        self.PreShutdown()
        time.sleep(180)
        C_Sys.RestartPC()


class Files:

    # Archives logs
    def LogArch(self):
        listForArchiving = []
        # Lists files stored in a directory
        for file in os.listdir(Config.logPath):
            # Continues to work only with files with the .log extension
            if re.search('log', file):
                # Checks the creation date of log files
                logDate = datetime.datetime.strptime(re.findall(r'\d{4}-\d{2}-\d{2}', file)[0], "%Y-%m-%d")
                if logDate.date() < date.today():
                    archName = str(logDate.date())
                    LOG.CMSLogger( 'Marked for archiving ' + file)
                    listForArchiving.append(file)
        # Checks if the folder that I'm going to create exists
        if listForArchiving and not os.path.exists(Config.logPath + str(date.today())):
            os.mkdir(Config.logPath + archName)
            # Move logs to folder
            for file in listForArchiving:
                shutil.move(Config.logPath + file, Config.logPath + archName + '\\' + file)
                LOG.CMSLogger( 'Moved to archive ' + file)
            # Archives a folder
            shutil.make_archive(base_name=Config.logPath + archName, format='zip', root_dir=Config.logPath + archName, )
            shutil.rmtree(Config.logPath + archName)
        else:
            LOG.CMSLogger( 'No logs found to archive')

    # Removes obsolete logs
    def LogDel(self):
        listForDeleting = []

        # Lists files stored in a directory
        for file in os.listdir(Config.logPath):
            # Continues to work only with files with the .zip extension
            if re.search('zip', file):
                # Checks the date the archive was created
                if (datetime.datetime.strptime(re.findall(r'\d{4}-\d{2}-\d{2}', file)[0], "%Y-%m-%d").date() - date.today()).days < -90:
                    listForDeleting.append(file)

        # Removes obsolete archives
        for file in listForDeleting:
            os.remove(Config.logPath + file)
            LOG.CMSLogger('File deleted ' + file)



class SysInit(Files):
    def InitCMS(self, Q_Internal):
        self.LogArch()
        self.LogDel()
        data = self.CheckSelf()
        if data == True:
            self.CheckLastSelfInitStd(Q_Internal)
        else:
            pass
        self.PutSysRun(Q_Internal)
        self.CheckLastStd(Q_Internal)




    def CheckDB(self):
        data = True
        if os.path.exists(Config.DBFolder):
            if os.path.exists(Config.DBPath):
                LOG.CMSLogger('Database file exist')
            else:
                handle = Database.DBFoo()
                handle.CreateTables()
                data = False
                LOG.CMSLogger('Database file created')
        else:
            os.mkdir(Config.DBFolder)
            handle = Database.DBFoo()
            handle.CreateTables()
            data = False
            LOG.CMSLogger('Database file created')
        return data

    def CheckSelf(self):
        data = self.CheckDB()
        return data

    def PutSysRun(self, Q_out):
        O_DBPrep = Database.Prepare()
        Q_out.put(O_DBPrep.SystemRunPrep(datetime.datetime.now()))


    def CheckLastSelfInitStd(self, Q_Internal):
        table = Database.Tables()
        crMsg = R.CreateMessage()
        try:
            lastStd = table.SelfInitShutdown().select().order_by(table.SelfInitShutdown.id.desc()).get()
        except:
            lastStd = None
        if lastStd:
            count = table.SelfInitShutdown().select().where(
                (table.SelfInitShutdown.datetime.year == datetime.date.today().year) &
                (table.SelfInitShutdown.datetime.month == datetime.date.today().month) &
                (table.SelfInitShutdown.datetime.day == datetime.date.today().day)).count()
            if lastStd.datetime.date() == datetime.datetime.now().date():
                if (datetime.datetime.now() - lastStd.datetime).seconds <= 300:
                    if count >= 3:
                        Q_Internal.put(crMsg.SetFlagUAV_0())
                        Q_Internal.put(crMsg.SetFlagCont_0())

                        msg = 'Exceeded quantity ' \
                                'Attempts to restart the system: {} ' \
                                'Last reboot: {} '.format(count, lastStd.datetime)

                        Q_Internal.put(crMsg.SendMail(msg))
                        LOG.CMSLogger(msg)
                        LOG.CMSLogger('Restart prohibited ')
                    else:
                        Q_Internal.put(crMsg.SetFlagUAV_1())
                        Q_Internal.put(crMsg.SetFlagCont_1())

                        msg = 'The frequency of attempts to ' \
                              'restart the system has been exceeded ' \
                                        'Last reboot: {} '.format(lastStd.datetime)

                        LOG.CMSLogger(msg)
                elif count >= 5:
                    Q_Internal.put(crMsg.SetFlagUAV_1())
                    Q_Internal.put(crMsg.SetFlagCont_1())

                    msg = 'The frequency of attempts to ' \
                          'restart the system has been exceeded ' \
                          'Last reboot: {} '.format(lastStd.datetime)

                    Q_Internal.put(crMsg.SendMail(msg))
                    LOG.CMSLogger(msg)

                    LOG.CMSLogger('Restart prohibited')
                else:
                    Q_Internal.put(crMsg.SetFlagUAV_2())
                    Q_Internal.put(crMsg.SetFlagCont_2())

                    LOG.CMSLogger('Restart allowed')
            else:
                Q_Internal.put(crMsg.SetFlagUAV_2())
                Q_Internal.put(crMsg.SetFlagCont_2())

                LOG.CMSLogger('Restart allowed')
        else:
            Q_Internal.put(crMsg.SetFlagUAV_2())
            Q_Internal.put(crMsg.SetFlagCont_2())

            LOG.CMSLogger('No data on system reboots')
            LOG.CMSLogger('Restart allowed')


    def CheckLastStd(self, Q_Internal):
        CreateMess = R.CreateMessage()
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        evTypes = {win32con.EVENTLOG_INFORMATION_TYPE: 'EVENTLOG_INFORMATION_TYPE',
                    win32con.EVENTLOG_WARNING_TYPE: 'EVENTLOG_WARNING_TYPE',
                    win32con.EVENTLOG_ERROR_TYPE: 'EVENTLOG_ERROR_TYPE'}

        machine = None
        logType = 'System'
        handle = win32evtlog.OpenEventLog(machine, logType)
        evSource = ['User32', 'Microsoft-Windows-Winlogon', 'Microsoft-Windows-Kernel-Power',
                  'Microsoft-Windows-Kernel-Boot',
                  'EventLog', 'Kernel-Boot']

        event = 1

        table = Database.Tables()

        currentRun = table.SystemRun().select().order_by(table.SystemRun.id.desc()).get()
        # lastInit = table.SystemInit().select().order_by(table.SystemInit.id.desc()).get()
        lastStd = table.SelfInitShutdown().select().where(
            table.SelfInitShutdown.key == ('reboot' or 'shutdown')).order_by(table.SelfInitShutdown.id.desc()).get()
        preCurrentRun = table.SystemRun().select().where(table.SystemRun.id == currentRun.id - 1).get()
        timeLine = (datetime.datetime.now() - preCurrentRun.datetime).seconds


        if lastStd.id != preCurrentRun.id:
            msgTxt = 'Предыдущее отключение не было инициировано CMS, либо произошел сбой записи в БД \n'
            while event:
                try:
                    event = win32evtlog.ReadEventLog(handle, flags, 0)
                    for ev_obj in event:

                        the_time = ev_obj.TimeGenerated
                        if (datetime.datetime.now() - the_time).seconds <= timeLine:

                            if str(ev_obj.SourceName) in evSource:
                                cat = str(ev_obj.EventCategory)
                                src = str(ev_obj.SourceName)
                                evt_type = str(evTypes[ev_obj.EventType])
                                msg = str(win32evtlogutil.SafeFormatMessage(ev_obj, logType))
                                evt_id = str(winerror.HRESULT_CODE(ev_obj.EventID))

                                if src == 'User32' and evt_id == '1074':

                                    if re.findall(r'RuntimeBroker.exe', msg):
                                        if re.findall(r'Перезапустить', msg):
                                            msgTxt += 'Система была перезагружена пользователем, \n' \
                                                        'Время: {}, \n' \
                                                        'Тип: {}, \n' \
                                                        'Источник: {}, \n' \
                                                        'Код события: {}, \n' \
                                                        'Описание: {} '.format(the_time.Format(), evt_type, src, evt_id, msg)


                                        elif re.findall(r'Выключение питания', msg):
                                            msgTxt += 'Система была выключена пользователем, ' \
                                                      'Время: {}, \n' \
                                                      'Тип: {}, \n' \
                                                      'Источник: {}, \n' \
                                                      'Код события: {}, \n' \
                                                      'Описание: {} '.format(the_time.Format(), evt_type, src, evt_id,
                                                                             msg)
                                        break



                except:
                   pass
            if msgTxt:
                LOG.CMSLogger(msgTxt)
                Q_Internal.put(CreateMess.SendMail(msgTxt))
            win32evtlog.CloseEventLog(handle)

