#v.1.1.0

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
logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')

class System:

    def LogArchiever(self):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
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
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Closed')


    def LogDeleter(self):
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

    def TempDeleter(self):
        for file in os.listdir(Config.tempPath):
            os.remove('{}{}'.format(Config.tempPath, file))
            logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Файл удален ' + file)


    def CMSUpgrade(self):

        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        priorities = {'GLOBAL': 0, 'GROUP': 0, 'LOCAL': 0}
        versions = {'GLOBAL': 0, 'GROUP': 0, 'LOCAL': 0, 'CURRENT':0}

        if Config.upgradePolitic == 1:
            # Чтение текщей версии
            if os.path.exists(os.path.dirname(__file__) + '\\PACKAGE.ver'):
                file = open(os.path.dirname(__file__) + '\\PACKAGE.ver', 'r')
                currentV = file.read()
                file.close()
                versions['CURRENT'] = currentV

            priorities['GLOBAL'], versions['GLOBAL'] = self.CheckCMSUpdates(Config.globalCmsRenew, 'GLOBAL')
            priorities['GROUP'], versions['GROUP'] = self.CheckCMSUpdates(Config.groupCmsRenew, 'GROUP')
            priorities['LOCAL'], versions['LOCAL'] = self.CheckCMSUpdates(Config.localCmsRenew, 'LOCAL')

            maxPriority = sorted(priorities, key=priorities.__getitem__)[-1]
            logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Определен приоритет каталога обновлений: ' + maxPriority)
            print(priorities[maxPriority])
            if priorities[maxPriority] > 200:
                currentVArr = versions['CURRENT'].split('.')
                newtVArr = versions[maxPriority].split('.')

                # Сравнение версий
                stopCheck = 0
                if currentVArr[0] == newtVArr[0]:
                    if currentVArr[1] == newtVArr[1]:
                        if currentVArr[2] == newtVArr[2]:
                            logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Не обнаружено обновлений')
                        elif int(currentVArr[2]) < int(newtVArr[2]):
                            logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Обнаружено обновление ' + versions[maxPriority])
                            self.CurrentCMSArch(currentV)
                            self.RenewCMSFiles(Config.globalCmsRenew)
                            stopCheck = 1
                    elif int(currentVArr[1]) < int(newtVArr[1]) and stopCheck != 1:
                        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Обнаружено обновление ' + versions[maxPriority])
                        self.CurrentCMSArch(currentV)
                        self.RenewCMSFiles(Config.groupCmsRenew)
                elif  int(currentVArr[0]) < int(newtVArr[0]) and stopCheck != 1:
                    logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Обнаружено обновление ' + versions[maxPriority])
                    self.CurrentCMSArch(currentV)
                    self.RenewCMSFiles(Config.globalCmsRenew)
            else:
                logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Приоритет недостаточен. Отмена обновления.')
        else:
            pass
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Closed')

    def CheckCMSUpdates(self, path, type):

        upgradeScoreKey = {'IGNORE': 0, 'FREE': 200, 'FORCE': 300, 'LOCK': 400}
        upgradeScoreType = {'GLOBAL': 30, 'GROUP': 20, 'LOCAL': 10}
        upgradeScoreTypeLock = {'GLOBAL': 10, 'GROUP': 20, 'LOCAL': 30}

        if os.path.exists(path + 'PACKAGE.ver'):
            file = open(Config.globalCmsRenew + 'PACKAGE.ver', 'r')
            version = file.read()
            file.close()

            file = open(path + 'UPGRADE.key', 'r')
            key = file.read()
            file.close()

            score = upgradeScoreKey[key]
            if key == 'LOCK':
                score += upgradeScoreTypeLock[type]
            else:
                score += upgradeScoreType[type]
        else:
            score, version = 0, '0.0.0'
        return score, version

    def CurrentCMSArch(self, version):

        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')

        if  not os.path.exists(Config.CMSArchPath + str(version)):
            shutil.copytree(os.getcwd(), Config.CMSArchPath + str(version))
            logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Текщий пакет заархивирован')

        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Closed')

    def RenewCMSFiles(self, path):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        shutil.rmtree(os.path.dirname(__file__))
        shutil.copytree(path, os.path.dirname(__file__))

        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Обновление выполнено')
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Closed')

    def ContentRenewHandler(self):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        ContentRefresh.RenewHandler()
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Closed')


