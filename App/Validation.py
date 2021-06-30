#v.1.1.1

import re
import shutil
import psutil
from App.Config import Config
import os
import numpy as np
import pyautogui
import cv2
import time
from datetime import date
from App.Config import Config
from App import LogManager
import random
import os

class System:

    def LastShutdown(self):
        f = open('{}lastShutDown.txt'.format(Config.tempPath), 'r')
        lastShutDown = f.read()
        f.close()

    def NovaStudio(self):
        pathTarget = 'C:\\Users\\rUser_local\\AppData\\Roaming\\NovaStudio2012\\'
        pathSource = 'C:\\Users\\rUser_local\\AppData\\Roaming\\NovaStudio2012_bcp\\'
        fileName = 'sysinfo.bin'
        search = 'zh-CN'
        x = 0
        x5 = 0
        for proc in psutil.process_iter():
            processName = proc.as_dict(attrs=['name'])
            processPid = proc.as_dict(attrs=['pid'])
            if processName['name'] == 'NovaStudio.exe':
                x5 = 1
                isNovaBin = os.path.exists(pathTarget + fileName)
                if isNovaBin == True:
                    try:
                        file = open(pathTarget + fileName, 'rb')
                        string = file.read()
                        isMatсh = re.search(search, str(string))
                    except:

                        x = 1
                    if isMatсh == None:
                        pass
                    else:
                        x = 1
                        novaProcess = psutil.Process(processPid['pid'])
                        for child in novaProcess.children(recursive=True):
                            child.kill()
                        novaProcess.kill()
                else:
                    x = 1
            else:
                pass
        if x == 1:
            shutil.copy(pathSource + fileName, pathTarget + fileName)
            try:
                pass
            except:
                pass
            try:
                f = open('{}lastShutDown.txt'.format(Config.tempPath, 'w'))
                f.write('1')
                f.close()
            except:
                pass
        return x5

    def ScreenValidation(self):
        # Запись статуса вхождения пользователя
        d = date.today()
        userStateFile = open('{}userState.txt'.format(Config.tempPath, str(d)), 'w')
        userStateFile.write('1')
        userStateFile.close()
        chanelSumArr = []

        if Config.screenNum == 1:  # По количеству областей будет допиливться
            while True:
                while len(chanelSumArr) < 2:
                    # Функциональная часть снимка экрана и подсчета интнсивности каналов
                    screenShot = pyautogui.screenshot(region=(Config.regiondict[0]))  # Снимок экрана
                    chanelIntens = cv2.cvtColor(np.array(screenShot),
                                                cv2.COLOR_RGB2BGR)  # передача изображения на анализ каналов
                    commonIntens = chanelIntens.sum(axis=2)  # посмотреть что делает эта строка
                    chanelSum = np.sum(commonIntens)  # Сумма интенсивности по каналам
                    if len(chanelSumArr) < 2:
                        chanelSumArr.append(chanelSum)
                # Часть проверок значений, записи состояний
                if len(chanelSumArr) == 2:
                    f = open('{}screenState.txt'.format(Config.tempPath), 'w')  # Пишу состояние экрана
                    if (chanelSumArr[0] == chanelSumArr[1]):
                        f.write('1')
                    else:
                        f.write('0')
                    f.close()
                    del chanelSumArr[0]  # Удаляю из словаря запись с индексом 0

                time.sleep(random.randint(30, 90))
        else:
            pass

    def CheckScreenValidationData(self):
        # количество итераций цикла с отсутсвием вхождения пользователя
        userNotLoggedInCount = 0
        # Статус вхождния пользователя
        userState = '0'
        # количество итераций цикла с отсутсвием движения экрана
        scrFreezCount = 0
        # количество итераций цикла с отсутсвием запуска валидатора
        scrNotRunCount = 0
        while True:
            # ПРОВЕРКА ВХОЖДЕНИЯ ПОЛЬЗОВАТЕЛЯ
            if userState == '0':
                f = open('{}userState.txt'.format(Config.tempPath), 'r')
                userState = f.read()
                f.close()
                userNotLoggedInCount += 1
                if userNotLoggedInCount > 30:
                    userNotLoggedInCount = 0
                if (userState == '1'):
                    userNotLoggedInCount = 0

            else:
                # Проверяет состояние экрана
                isStateFile = os.path.exists('{}screenState.txt'.format(Config.tempPath))
                if isStateFile == True:
                    f = open('{}screenState.txt'.format(Config.tempPath), 'r')
                    screenState = f.read()
                    f.close()
                    if screenState == '0':
                        scrFreezCount = 0
                    if screenState == '2':
                        scrNotRunCount += 1
                        if scrNotRunCount >= 40:
                            scrNotRunCount = 0
                    else:
                        scrFreezCount += 1
                        if scrFreezCount >= 45:
                            scrFreezCount = 0

                else:
                    pass
            time.sleep(10)