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
from App import Resource, API, LogManager, Database

LOG = LogManager.Log_Manager()

class Init:
    def __init__(self):
        global Nova
        global Win
        global Sys
        Nova = API.Nova()
        Win = API.Process()
        Sys = API.System()


class Process(Init):

    def Start(self, data):
        if data == Resource.ProcList[0]:
            Nova.RunNova()

    def Terminate(self, data):
        if data == Resource.ProcList[1]:
            Nova.TerminateMars()
        if data == Resource.ProcList[0]:
            Nova.TerminateNova()

    def Restart(self, data):
        if data == Resource.ProcList[0]:
            Nova.RestartNova()

class System(Init):

    def RebootInit(self):
        time.sleep(180)
        Sys.RestartPC()






class Files:
    def RestoreNovaBin(self):
        if self.CheckNovaFile() == True:
            if Nova.GetProcState(Resource.ProcList[0]) == True:
                Nova.TerminateNova()
                self.CopyNovaBin()


    def CheckNovaFile(self):
        file = open(Resource.novaBinFile, 'rb')
        string = file.read()
        return re.search('zh-CN', str(string))

    def CopyNovaBin(self):
        shutil.copy(Resource.novaBinFileBak,  Resource.novaBinFile)



    # Архивирует логи
    def LogArch(self):
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

    # Удаляет устаревшие логи
    def LogDel(self):
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
                        Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[9],
                                        Resource.root[3]: Resource.ShutdownFlagData[0]})
                        Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[10],
                                        Resource.root[3]: Resource.ShutdownFlagData[0]})

                        LOG.CMSLogger( 'Превышено количество '
                                        'попыток перезапустить систему: {} '
                                        'Последняя перезагрузка: {} '.format(count, lastReboot))
                        LOG.CMSLogger( 'Перезагрузка запрещена ')

                    else:
                        Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[9],
                                        Resource.root[3]: Resource.ShutdownFlagData[1]})
                        Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[10],
                                        Resource.root[3]: Resource.ShutdownFlagData[1]})

                        LOG.CMSLogger('Превышена '
                                        'частота попыток перезапустить систему '
                                        'Последняя перезагрузка: {} '.format(lastReboot))
                elif count >= 5:
                    Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[9],
                                    Resource.root[3]: Resource.ShutdownFlagData[1]})
                    Q_Internal.put({Resource.root[1]: Resource.Head[4], Resource.root[2]: Resource.Key[10],
                                    Resource.root[3]: Resource.ShutdownFlagData[1]})

                    LOG.CMSLogger( 'Превышена '
                                   'частота попыток перезапустить систему '
                                   'Последняя перезагрузка: {} '.format(lastReboot))
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


