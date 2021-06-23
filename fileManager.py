import config
import datetime
from datetime import date
import os
import re
import shutil


class fileCleaner:

    def logArchiever(self):

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
            shutil.rmtree(config.logPath + str(date.today()))


    def logDeleter(self):
        listForDeleting = []


        # Перечисляю файлы, хранящиеся в дирректории
        for file in os.listdir(config.logPath):
            # Продолжаю работать только с файлами с расширением .zip
            if re.search('zip', file):
                # Проверяю дату создания архива
                if (datetime.datetime.strptime(re.findall(r'\d{4}-\d{2}-\d{2}', file)[0], "%Y-%m-%d").date() - date.today()).days < -90:
                    # Удаляю устаревший архив
                    os.remove(config.logPath + file)


test = fileCleaner()
test.logDeleter()






# a = '2010-05-31'
#
# datee = datetime.datetime.strptime(a, "%Y-%m-%d")
#
#
# print(datee.month)

