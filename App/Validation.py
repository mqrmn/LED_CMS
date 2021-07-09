#v.1.1.1

import re
import shutil
import psutil
from App.Config import Config

import numpy as np
import pyautogui
import cv2
import time
from App.Config import Config
import random
import os
from App import Communicate

class System:

    # Проверка последнего отключения системы
    def LastShutdown(self):
        f = open('{}lastShutDown.txt'.format(Config.tempPath), 'r')
        lastShutDown = f.read()
        f.close()

    # Проверка состояния файла NovaStudio
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

    def test(self):
        e = 0
        while e < 2:
            print('TEST')
            time.sleep(10)
            e += 1

    # Создание скриншотов, проверка экрана на статичность
    def GetScreenValidation(self, screenStateQueue):
        chanelSumArr = []
        if Config.screenNum == 1:  # По количеству областей будет допиливаться
            while True:
                while len(chanelSumArr) < 2:
                    screenShot = pyautogui.screenshot(region=(Config.regiondict[0]))            # Снимок экрана
                    chanelIntens = cv2.cvtColor(np.array(screenShot), cv2.COLOR_RGB2BGR)        # передача изображения на анализ каналов
                    commonIntens = chanelIntens.sum(axis=2)                                     # посмотреть что делает эта строка
                    chanelSum = np.sum(commonIntens)                                            # Сумма интенсивности по каналам
                    if len(chanelSumArr) < 2:
                        chanelSumArr.append(chanelSum)

                # Проверка значений, передача результата в очередь
                if len(chanelSumArr) == 2:
                    if (chanelSumArr[0] == chanelSumArr[1]):                                    # Экран статичен
                        screenStateQueue.put(1)
                        # print('screenStateQueue.put(1)')
                    else:
                        # print('screenStateQueue.put(0)')
                        screenStateQueue.put(0)
                    del chanelSumArr[0]                                                         # Удаляю из словаря запись с индексом 0
                time.sleep(random.randint(10, 20))
        else:
            pass

    # Счетчик статичности экрана
    def CheckScreenValidation(self, screenStateQueue):
        screenFreezeCount = 0
        checkCount = 0
        Network_ = Communicate.Network()            # Экземпляр класса для передачи состояния службе
        while True:
               # Принимает данные из очереди
            if screenStateQueue.empty() == True:
                time.sleep(5)
            else:
                screenState = screenStateQueue.get()
                # print('screenState', screenState)
                if screenState == 0:                    # Проверяет состояние экрана
                    pass
                if screenState == 1:
                    screenFreezeCount += 1
                checkCount += 1
                # print('checkCount', checkCount)
                # print('screenFreezeCount', screenFreezeCount)
                if checkCount >= 2:
                    if screenFreezeCount == checkCount:
                        screenFreezeCount = 1
                    else:
                        screenFreezeCount = 0
                    Network_.Client(Config.localhost, Config.CMSCoreInternalPort, ['CheckScreenValidation', screenFreezeCount])
                    screenFreezeCount, checkCount = 0, 0


    def CoreScreenValidation(self, ScreenValidationQueue, ExecutionQueue):
        count = 0
        while True:
            if ScreenValidationQueue.empty() == False:
                if ScreenValidationQueue.get() == '1':
                    count += 1
                    print('CoreScreenValidation count', count)

                else:

                    count = 0
                    print('CoreScreenValidation count', count)
            if count >= 2:
                print('''ExecutionQueue.put(['CoreScreenValidation', '1'])''')
                ExecutionQueue.put(['CoreScreenValidation', '1'])
                count = 0