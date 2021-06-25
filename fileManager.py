import config
import datetime
from datetime import date
import os
import re
import shutil
import logManager
import contentRefresh


class fileCleaner:

    def logArchiever(self):
        logManager.cmsLogger('')
        listForArchiving = []

        # Перечисляю файлы, хранящиеся в дирректории
        for file in os.listdir(config.logPath):
            # Продолжаю работать толь с файлами с расширением .log
            if re.search('log', file):
                # Проверяю дату создания лог файлов
                if datetime.datetime.strptime(re.findall(r'\d{4}-\d{2}-\d{2}', file)[0], "%Y-%m-%d").month < date.today().month:
                    listForArchiving.append(file)
        # Проверяю существует ли папка которую собираюсь создать
        if not os.path.exists(config.logPath + str(date.today())):
            os.mkdir(config.logPath + str(date.today()))
            # Перемещаю журналы в папку
            for file in listForArchiving:
                shutil.move(config.logPath + file, config.logPath + str(date.today()) + '\\' + file)
            # Архивирую папку
            shutil.make_archive(base_name=config.logPath + str(date.today()), format='zip', root_dir=config.logPath + str(date.today()),  )

            logManager.cmsLogger('Создан архив журналов {}'.format(config.logPath + str(date.today())))

            shutil.rmtree(config.logPath + str(date.today()))


    def logDeleter(self):
        listForDeleting = []

        # Перечисляю файлы, хранящиеся в дирректории
        for file in os.listdir(config.logPath):
            # Продолжаю работать только с файлами с расширением .zip
            if re.search('zip', file):
                # Проверяю дату создания архива
                if (datetime.datetime.strptime(re.findall(r'\d{4}-\d{2}-\d{2}', file)[0], "%Y-%m-%d").date() - date.today()).days < -90:
                    logManager.cmsLogger()
                    listForDeleting.append(file)

        # Удаляю устаревшие архивы
        for file in listForDeleting:
            os.remove(config.logPath + file)
            logManager.cmsLogger('Удален архив журналов {}'.format(config.logPath + file))

    def tempDeleter(self):
        for tempFile in os.listdir(config.tempPath):
            os.remove('{}{}'.format(config.tempPath, tempFile))

class fileRenewer:

    def cmsRenewer(self):
        yaListGroupRenew = os.listdir(config.groupCmsRenew)
        yaListLocalRenew = os.listdir(config.localCmsRenew)

        renewStatus = 0

        if yaListGroupRenew:
            renewStatus = 1
            for file in yaListGroupRenew:
                shutil.copy(config.groupCmsRenew + file, config.cmsLocalPath + file)
                logManager.cmsLogger('Обновление CMS из групповой папки: {}'.format(file))

        if yaListLocalRenew:
            renewStatus = 1
            for file in yaListLocalRenew:
                shutil.move(config.localCmsRenew + file, config.cmsLocalPath + file)
                logManager.cmsLogger('Обновление CMS из локальной папки: {}'.format(file))

        if renewStatus == 1:
            logManager.cmsLogger('Выполнено обновление CMS')
        else:
            logManager.cmsLogger('Нет файлов для обновления CMS')

    def contentRenewHandler(self):
        contentRefresh.renewHandler()
