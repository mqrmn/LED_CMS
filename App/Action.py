# 1.1.1

import sys
import psutil
import time
import wmi
import pythoncom
import os
import shutil
from inspect import currentframe, getframeinfo
import re
import datetime
from datetime import date

sys.path.append("C:\\MOBILE\\Local\\CMS")
from App.Config import Config
from App import Resource, API, LogManager, Database

logging = LogManager._Log_Manager_()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])

class Process:

    def Start(self, data):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        if data == Resource.ProcList[0]:
            self.RunNova()

    def Terminate(self, data):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        if data == Resource.ProcList[1]:
            self.TerminateMars()
        if data == Resource.ProcList[0]:
            self.TerminateNova()

    def Restart(self, data):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        if data == Resource.ProcList[0]:
            self.RestartNova()

    def RestartNova(self):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        self.TerminateNova()
        self.RunNova()

    def RunNova(self):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        pythoncom.CoInitialize()
        handle = wmi.WMI()
        handle.Win32_Process.Create(CommandLine='C:\\Program Files (x86)\\NovaStudio\\Bin\\NovaStudio.exe', )

    def TerminateNova(self):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        pythoncom.CoInitialize()
        handle = wmi.WMI()
        for proc in handle.Win32_Process(Name=Resource.ProcList[0]):
            proc.Terminate(Reason=1)

    def TerminateMars(self):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
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
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
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
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        listForArchiving = []
        # Перечисляю файлы, хранящиеся в дирректории
        for file in os.listdir(Config.logPath):
            # Продолжаю работать толь с файлами с расширением .log
            if re.search('log', file):
                # Проверяю дату создания лог файлов
                if datetime.datetime.strptime(re.findall(r'\d{4}-\d{2}-\d{2}', file)[0], "%Y-%m-%d").day < date.today().day:
                    logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Помечен для архивирования ' + file)
                    listForArchiving.append(file)
        # Проверяю существует ли папка которую собираюсь создать
        if listForArchiving and not os.path.exists(Config.logPath + str(date.today())):
            os.mkdir(Config.logPath + str(date.today()))
            # Перемещаю журналы в папку
            for file in listForArchiving:
                shutil.move(Config.logPath + file, Config.logPath + str(date.today()) + '\\' + file)
                logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Перемещен в архив ' + file)
            # Архивирую папку
            shutil.make_archive(base_name=Config.logPath + str(date.today()), format='zip', root_dir=Config.logPath + str(date.today()), )
            shutil.rmtree(Config.logPath + str(date.today()))
        else:
            logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Журналов для архивирования не обнаружено')
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Closed')

    # Удаляет устаревшие логи
    def LogDel(self):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
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
            logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Файл удален ' + file)
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Closed')

class Init(Files):
    def InitCMS(self, Q_Internal):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        self.LogArch()
        self.LogDel()
        data = self.CheckSelf()
        if data == True:
            self.CheckLastShutdown(Q_Internal)
        else:
            pass


    def CheckDB(self):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        data = True
        if os.path.exists(Config.DBFolder):
            if os.path.exists(Config.DBPath):
                logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Database file exist')
            else:
                handle = Database.DBFoo()
                handle.CreateTables()
                data = False
                logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Database file created')
        else:
            os.mkdir(Config.DBFolder)
            handle = Database.DBFoo()
            handle.CreateTables()
            data = False
            logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Database file created')
        return data

    def CheckSelf(self):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        data = self.CheckDB()
        return data

    def CheckLastShutdown(self, Q_Internal):
        table = Database.Tables()
        lastReboot = table.SelfInitShutdown().select().order_by(table.SelfInitShutdown.id.desc()).get()

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

                    logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Превышено количество '
                                                                                   'попыток перезапустить систему: {} '
                                                                                   'Последняя перезагрузка: {} '.format(count, lastReboot))
                    logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Перезагрузка запрещена')

                else:
                    Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[9],
                                    Resource.root[3]: Resource.ShutdownFlagData[1]})
                    Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[10],
                                    Resource.root[3]: Resource.ShutdownFlagData[1]})

                    logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Превышена'
                                                                                  'частота попыток перезапустить систему '
                                                                                  'Последняя перезагрузка: {} '.format(lastReboot))
            elif count >= 5:
                Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[9],
                                Resource.root[3]: Resource.ShutdownFlagData[1]})
                Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[10],
                                Resource.root[3]: Resource.ShutdownFlagData[1]})

                logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Превышена '
                                                                               'частота попыток перезапустить систему '
                                                                               'Последняя перезагрузка: {}'.format(lastReboot))
                logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Перезагрузка запрещена')
            else:
                Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[9],
                                Resource.root[3]: Resource.ShutdownFlagData[2]})
                Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[10],
                                Resource.root[3]: Resource.ShutdownFlagData[2]})

                logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Перезагрузка разрешена')
        else:
            Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[9],
                            Resource.root[3]: Resource.ShutdownFlagData[2]})
            Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[10],
                            Resource.root[3]: Resource.ShutdownFlagData[2]})

            logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Перезагрузка разрешена')



