# 1.1.1

import sys
import time
import os
import shutil
import re
import datetime
from datetime import date

sys.path.append("C:\\MOBILE\\Local\\CMS")
from App.Config import Config
from App import API, Log, Database
from App import Resource as R

LOG = Log.Log_Manager()

class Init:
    def __init__(self):
        global C_Nova
        global C_Win
        global C_Sys
        C_Nova = API.Nova()
        C_Win = API.Process()
        C_Sys = API.System()


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

    def RebootInit(self):
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
            self.CheckLastShutdown(Q_Internal)
        else:
            pass


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

    def CheckLastShutdown(self, Q_Internal):
        table = Database.Tables()
        try:
            lastReboot = table.SelfInitShutdown().select().order_by(table.SelfInitShutdown.id.desc()).get()
        except:
            lastReboot = None
        if lastReboot:
            count = table.SelfInitShutdown().select().where(
                (table.SelfInitShutdown.datetime.year == datetime.date.today().year) &
                (table.SelfInitShutdown.datetime.month == datetime.date.today().month) &
                (table.SelfInitShutdown.datetime.day == datetime.date.today().day)).count()
            if lastReboot.datetime.date() == datetime.datetime.now().date():
                if (datetime.datetime.now() - lastReboot.datetime).seconds <= 300:
                    if count >= 3:
                        Q_Internal.put({R.r[1]: R.H[4], R.r[2]: R.K[9],
                                        R.r[3]: R.ShutdownFlagData[0]})
                        Q_Internal.put({R.r[1]: R.H[4], R.r[2]: R.K[10],
                                        R.r[3]: R.ShutdownFlagData[0]})
                        LOG.CMSLogger('Exceeded quantity '
                                        'Attempts to restart the system: {} '
                                        'Last reboot: {} '.format(count, lastReboot))
                        LOG.CMSLogger('Restart prohibited ')
                    else:
                        Q_Internal.put({R.r[1]: R.H[4], R.r[2]: R.K[9],
                                        R.r[3]: R.ShutdownFlagData[1]})
                        Q_Internal.put({R.r[1]: R.H[4], R.r[2]: R.K[10],
                                        R.r[3]: R.ShutdownFlagData[1]})
                        LOG.CMSLogger('The frequency of attempts to restart the system has been exceeded '
                                        'Last reboot: {} '.format(lastReboot))
                elif count >= 5:
                    Q_Internal.put({R.r[1]: R.H[4], R.r[2]: R.K[9],
                                    R.r[3]: R.ShutdownFlagData[1]})
                    Q_Internal.put({R.r[1]: R.H[4], R.r[2]: R.K[10],
                                    R.r[3]: R.ShutdownFlagData[1]})
                    LOG.CMSLogger('The frequency of attempts to restart the system has been exceeded '
                                   'Last reboot: {} '.format(lastReboot))
                    LOG.CMSLogger('Restart prohibited')
                else:
                    Q_Internal.put({R.r[1]: R.H[4], R.r[2]: R.K[9],
                                    R.r[3]: R.ShutdownFlagData[2]})
                    Q_Internal.put({R.r[1]: R.H[4], R.r[2]: R.K[10],
                                    R.r[3]: R.ShutdownFlagData[2]})
                    LOG.CMSLogger('Restart allowed')
            else:
                Q_Internal.put({R.r[1]: R.H[4], R.r[2]: R.K[9],
                                R.r[3]: R.ShutdownFlagData[2]})
                Q_Internal.put({R.r[1]: R.H[4], R.r[2]: R.K[10],
                                R.r[3]: R.ShutdownFlagData[2]})
                LOG.CMSLogger('Restart allowed')
        else:
            Q_Internal.put({R.r[1]: R.H[4], R.r[2]: R.K[9],
                            R.r[3]: R.ShutdownFlagData[2]})
            Q_Internal.put({R.r[1]: R.H[4], R.r[2]: R.K[10],
                            R.r[3]: R.ShutdownFlagData[2]})
            LOG.CMSLogger('No data on system reboots')
            LOG.CMSLogger('Restart allowed')


