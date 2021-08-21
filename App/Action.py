# 1.1.1

import sys
import psutil
import time
import wmi
import pythoncom
import os
import shutil
import re
import datetime
from datetime import date

sys.path.append("C:\\MOBILE\\Local\\CMS")
from App.Config import Config
from App import Resource, API, LogManager, Database

LOG = LogManager.Log_Manager()

class Process:

    def Start(self, data):
        LOG.CMSLogger( 'Called')
        if data == Resource.ProcList[0]:
            self.RunNova()

    def Terminate(self, data):
        LOG.CMSLogger('Called')
        if data == Resource.ProcList[1]:
            self.TerminateMars()
        if data == Resource.ProcList[0]:
            self.TerminateNova()

    def Restart(self, data):
        LOG.CMSLogger('Called')
        if data == Resource.ProcList[0]:
            self.RestartNova()

    def RestartNova(self):
        LOG.CMSLogger('Called')
        self.TerminateNova()
        self.RunNova()

    def RunNova(self):
        LOG.CMSLogger( 'Called')
        pythoncom.CoInitialize()
        handle = wmi.WMI()
        handle.Win32_Process.Create(CommandLine='C:\\Program Files (x86)\\NovaStudio\\Bin\\NovaStudio.exe', )

    def TerminateNova(self):
        LOG.CMSLogger( 'Called')
        pythoncom.CoInitialize()
        handle = wmi.WMI()
        for proc in handle.Win32_Process(Name=Resource.ProcList[0]):
            proc.Terminate(Reason=1)

    def TerminateMars(self):
        LOG.CMSLogger('Called')
        pythoncom.CoInitialize()
        handle = wmi.WMI()
        handle.Win32_Process.Create(
            CommandLine='C:\\Users\\rAdmin_local\\AppData\\Roaming\\Nova Star\\NovaLCT\\Bin\\NovaLCT.exe', )
        time.sleep(15)
        for proc in psutil.process_iter():
            processName = proc.as_dict(attrs=['name'])
            processPid = proc.as_dict(attrs=['pid'])
            if processName['name'] == 'NovaLCT.exe':

                novaProcess = psutil.Process(processPid['pid'])
                for child in novaProcess.children(recursive=True):
                    child.kill()

                novaProcess.kill()

            else:
                pass


class Service:

    def Start(self):
        pass

    def Stop(self):
        pass

    def Restart(self):
        pass

class System:

    def Reboot(self):
        LOG.CMSLogger('Called')
        handle = API.Win()
        time.sleep(180)
        handle.RestartPC()

class Files:
    def RestoreNovaBin(self):
        C_API = API.Win()
        if self.CheckNovaFile() == True:
            if C_API.GetProcState(Resource.ProcList[0]) == True:
                Process.TerminateNova()
                self.CopyNovaBin()


    def CheckNovaFile(self):
        file = open(Resource.novaBinFile, 'rb')
        string = file.read()
        return re.search('zh-CN', str(string))

    def CopyNovaBin(self):
        shutil.copy(Resource.novaBinFileBak,  Resource.novaBinFile)

    # Архивирует логи
    def LogArch(self):
        LOG.CMSLogger( 'Called')
        listForArchiving = []
        # Перечисляю файлы, хранящиеся в дирректории
        for file in os.listdir(Config.logPath):
            # Продолжаю работать толь с файлами с расширением .log
            if re.search('log', file):
                # Проверяю дату создания лог файлов
                logDate = datetime.datetime.strptime(re.findall(r'\d{4}-\d{2}-\d{2}', file)[0], "%Y-%m-%d")
                if logDate.date() < date.today():
                    archName = str(logDate.date())
                    LOG.CMSLogger( 'Помечен для архивирования ' + file)
                    listForArchiving.append(file)
        # Проверяю существует ли папка которую собираюсь создать
        if listForArchiving and not os.path.exists(Config.logPath + str(date.today())):
            os.mkdir(Config.logPath + archName)
            # Перемещаю журналы в папку
            for file in listForArchiving:
                shutil.move(Config.logPath + file, Config.logPath + archName + '\\' + file)
                LOG.CMSLogger( 'Перемещен в архив ' + file)
            # Архивирую папку
            shutil.make_archive(base_name=Config.logPath + archName, format='zip', root_dir=Config.logPath + archName, )
            shutil.rmtree(Config.logPath + archName)
        else:
            LOG.CMSLogger( 'Журналов для архивирования не обнаружено')
        LOG.CMSLogger('Closed')

    # Удаляет устаревшие логи
    def LogDel(self):
        LOG.CMSLogger('Called')
        listForDeleting = []

        # Перечисляю файлы, хранящиеся в дирректории
        for file in os.listdir(Config.logPath):
            # Продолжаю работать только с файлами с расширением .zip
            if re.search('zip', file):
                # Проверяю дату создания архива
                if (datetime.datetime.strptime(re.findall(r'\d{4}-\d{2}-\d{2}', file)[0], "%Y-%m-%d").date() - date.today()).days < -90:
                    listForDeleting.append(file)

        # Удаляю устаревшие архивы
        for file in listForDeleting:
            os.remove(Config.logPath + file)
            LOG.CMSLogger('Файл удален ' + file)
        LOG.CMSLogger( 'Closed')

class Init(Files):
    def InitCMS(self, Q_Internal):
        LOG.CMSLogger( 'Called')
        self.LogArch()
        self.LogDel()
        data = self.CheckSelf()
        if data == True:
            self.CheckLastShutdown(Q_Internal)
        else:
            pass


    def CheckDB(self):
        LOG.CMSLogger( 'Called')
        data = True
        if os.path.exists(Config.DBFolder):
            if os.path.exists(Config.DBPath):
                LOG.CMSLogger( 'Database file exist')
            else:
                handle = Database.DBFoo()
                handle.CreateTables()
                data = False
                LOG.CMSLogger( 'Database file created')
        else:
            os.mkdir(Config.DBFolder)
            handle = Database.DBFoo()
            handle.CreateTables()
            data = False
            LOG.CMSLogger( 'Database file created')
        return data

    def CheckSelf(self):
        LOG.CMSLogger( 'Called')
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
                        Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[9],
                                        Resource.root[3]: Resource.ShutdownFlagData[0]})
                        Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[10],
                                        Resource.root[3]: Resource.ShutdownFlagData[0]})

                        LOG.CMSLogger( 'Превышено количество '
                                                                                       'попыток перезапустить систему: {} '
                                                                                       'Последняя перезагрузка: {} '.format(count, lastReboot))
                        LOG.CMSLogger( 'Перезагрузка запрещена')

                    else:
                        Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[9],
                                        Resource.root[3]: Resource.ShutdownFlagData[1]})
                        Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[10],
                                        Resource.root[3]: Resource.ShutdownFlagData[1]})

                        LOG.CMSLogger('Превышена'
                                                                                      'частота попыток перезапустить систему '
                                                                                      'Последняя перезагрузка: {} '.format(lastReboot))
                elif count >= 5:
                    Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[9],
                                    Resource.root[3]: Resource.ShutdownFlagData[1]})
                    Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[10],
                                    Resource.root[3]: Resource.ShutdownFlagData[1]})

                    LOG.CMSLogger( 'Превышена '
                                                                                   'частота попыток перезапустить систему '
                                                                                   'Последняя перезагрузка: {}'.format(lastReboot))
                    LOG.CMSLogger( 'Перезагрузка запрещена')
                else:
                    Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[9],
                                    Resource.root[3]: Resource.ShutdownFlagData[2]})
                    Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[10],
                                    Resource.root[3]: Resource.ShutdownFlagData[2]})

                    LOG.CMSLogger( 'Перезагрузка разрешена')
            else:
                Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[9],
                                Resource.root[3]: Resource.ShutdownFlagData[2]})
                Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[10],
                                Resource.root[3]: Resource.ShutdownFlagData[2]})

                LOG.CMSLogger('Перезагрузка разрешена')
        else:
            Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[9],
                            Resource.root[3]: Resource.ShutdownFlagData[2]})
            Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[10],
                            Resource.root[3]: Resource.ShutdownFlagData[2]})

            LOG.CMSLogger('Перезагрузка разрешена')


