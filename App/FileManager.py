#v.1.1.1

from App.Config import Config
import datetime
from datetime import date
import os
import re
import shutil
from App import LogManager, ContentRefresh
from inspect import currentframe, getframeinfo

logging = LogManager.LogManager()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])
logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Модуль запущен')

class System:

    def LogArchiever(self):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Метод вызван')
        listForArchiving = []
        # Перечисляю файлы, хранящиеся в дирректории
        for file in os.listdir(Config.logPath):
            # Продолжаю работать толь с файлами с расширением .log
            if re.search('log', file):
                # Проверяю дату создания лог файлов
                if datetime.datetime.strptime(re.findall(r'\d{4}-\d{2}-\d{2}', file)[0], "%Y-%m-%d").month < date.today().month:
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

        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Работа метода завершена без ошибок')


    def LogDeleter(self):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Метод вызван')
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

        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Работа метода завершена без ошибок')


    def TempDeleter(self):
        for file in os.listdir(Config.tempPath):
            os.remove('{}{}'.format(Config.tempPath, file))
            logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Файл удален ' + file)




    def CMSUpgrade(self):

        upgradeKeys = {'IGNORE': 100, 'FREE':200, 'FORCE':300, 'LOCK':400}
        priorities = {'GLOBAL': 0, 'GROUP': 0, 'LOCAL': 0}
        versions = {'GLOBAL': 0, 'GROUP': 0, 'LOCAL': 0, 'CURRENT':0}

        currentVArr = []
        newtVArr = []

        globalKey = None
        groupKey = None
        localKey = None

        globalEx = None
        groupEx = None
        localEx = None

        globalV = None
        groupV = None
        localV = None

        globalCMS = 0
        groupCMS = 0
        localCMS = 0

        if Config.upgradePolitic == 1:
            if os.path.exists(os.path.dirname(__file__) + '\\PACKAGE.ver'):
                print('1')
                file = open(os.path.dirname(__file__) + '\\PACKAGE.ver', 'r')
                currentV = file.read()
                file.close()
                versions['CURRENT'] = currentV

            if os.path.exists(Config.globalCmsRenew + 'PACKAGE.ver'):
                globalEx = 1
                file = open(Config.globalCmsRenew + 'PACKAGE.ver', 'r')
                globalV = file.read()
                file.close()

                versions['GLOBAL'] = globalV
                file = open(Config.globalCmsRenew + 'UPGRADE.key', 'r')
                globalKey = file.read()
                file.close()
                globalCMS = upgradeKeys[globalKey]

                if globalKey == 'LOCK':
                    globalCMS += 10
                else:
                    globalCMS += 30
                priorities['GLOBAL'] = globalCMS


            else:
                priorities['GLOBAL'] = globalCMS

            if os.path.exists(Config.groupCmsRenew + 'PACKAGE.ver'):
                groupEx = 1
                file = open(Config.groupCmsRenew + 'PACKAGE.ver', 'r')
                groupV = file.read()
                file.close()
                versions['GROUP'] = groupV
                file = open(Config.groupCmsRenew + 'UPGRADE.key', 'r')
                groupKey = file.read()
                file.close()
                groupCMS = upgradeKeys[groupKey]

                if groupKey == 'LOCK':
                    groupCMS += 20
                else:
                    groupCMS += 20


                priorities['GROUP'] = groupCMS
            else:
                priorities['GROUP'] = groupCMS

            if os.path.exists(Config.localCmsRenew + 'PACKAGE.ver'):
                localEx = 1
                file = open(Config.localCmsRenew + 'PACKAGE.ver', 'r')
                localV = file.read()
                file.close()
                versions['LOCAL'] = localV
                file = open(Config.localCmsRenew + 'UPGRADE.key', 'r')
                localKey = file.read()
                file.close()
                localCMS = upgradeKeys[localKey]

                if localKey == 'LOCK':
                    localCMS += 30
                else:
                    localCMS += 10


                priorities['LOCAL'] = localCMS
            else:
                priorities['LOCAL'] = localCMS

            print(priorities)
            maxPriority = sorted(priorities, key=priorities.__getitem__)[-1]
            print(maxPriority, versions['CURRENT'], versions[maxPriority])
            currentVArr = versions['CURRENT'].split('.')
            newtVArr = versions[maxPriority].split('.')

            if currentVArr[0] == newtVArr[0]:
                if currentVArr[1] == newtVArr[1]:
                    if currentVArr[2] == newtVArr[2]:
                        print('РАВНЫ')
                    elif int(currentVArr[2]) < int(newtVArr[2]):
                        print('ТЕКУЩАЯ НИЖЕ')
                        self.CurrentCMSArch(currentV)
                        self.RenewCMSFiles(Config.globalCmsRenew)
                elif int(currentVArr[1]) < int(currentV):
                    self.CurrentCMSArch(currentV)
                    self.RenewCMSFiles(Config.groupCmsRenew)
                    print('ТЕКУЩАЯ НИЖЕ')
            elif  int(currentVArr[0]) < int(newtVArr[0]):
                self.CurrentCMSArch(currentV)
                self.RenewCMSFiles(Config.globalCmsRenew)
                print('ТЕКУЩАЯ НИЖЕ')

        else:
            pass


    def CurrentCMSArch(self, version):

        if  not os.path.exists(Config.CMSArchPath + str(version)):
            shutil.copytree(os.getcwd(), Config.CMSArchPath + str(version))

    def RenewCMSFiles(self, path):
        shutil.rmtree(os.path.dirname(__file__))
        shutil.copytree(path, os.path.dirname(__file__))

    def ContentRenewHandler(self):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Метод вызван')
        ContentRefresh.RenewHandler()
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Работа метода завершена без ошибок')


