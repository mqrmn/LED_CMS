# 1.1.1

import sys
import re
import shutil
import psutil
import numpy as np
import pyautogui
import cv2
import time
import random
import os
import threading
import datetime
import pythoncom
import datetime
from inspect import currentframe, getframeinfo

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config
from App import API, Resource, LogManager, Action, Database


logging = LogManager._Log_Manager_()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])


class _System_:



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

    # Создание скриншотов, проверка экрана на статичность
    def GetScreenStatic(self, screenStateQueue):
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
                        screenStateQueue.put({'key': Resource.ComDict['key'][0], 'data': [Resource.ComDict['data'][Resource.ComDict['key'][0]][0], True], })
                    else:
                        screenStateQueue.put({'key': Resource.ComDict['key'][0], 'data': [Resource.ComDict['data'][Resource.ComDict['key'][0]][0], False], })
                    del chanelSumArr[0]                                                         # Удаляю из словаря запись с индексом 0
                time.sleep(random.randint(Config.timeoutSCheck[0], Config.timeoutSCheck[1]))
        else:
            pass

    def GetProcessState(self, Q_ProcState_):
        _WinApi_ = API.Win()
        while True:
            T_GetProcessState = threading.Thread(target=_WinApi_.GetProcessState, args=(Q_ProcState_,))
            T_GetProcessState.start()
            T_GetProcessState.join()
            time.sleep(Config.timeoutPCheck)

    def Threads(self, Threads):
        state = []
        for i in Threads:
            state.append(i.is_alive())
        return state

    def UAValid(self, Q_in, Q_Internal, Q_UAValidSF):

        C_Action = Action.System()
        C_Prepare = Database.Prepare()
        data = datetime.datetime.now()
        table = Database.Tables()
        count = 0
        while True:
            if Q_UAValidSF.empty() == False:
                FLAG = Q_UAValidSF.get()
            else:
                pass
            if Q_in.empty() == False:
                data = Q_in.get()
                if count == 0:
                    Q_Internal.put(C_Prepare.SystemInit(datetime.datetime.now()))
                    count += 1
            else:

                if ((datetime.datetime.now() - data).seconds) >= 20:


                    pythoncom.CoInitialize()

                    print('UAValid', 'FLAG', FLAG)
                    if FLAG > 0:
                        if FLAG > 1:
                            # C_Action.Reboot()
                            Q_Internal.put(C_Prepare.SelfInitShutdown(getframeinfo(currentframe())[2], 'reboot', datetime.datetime.now()))
                            logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'reboot')
                            break
                        else:
                            lastReboot = table.SelfInitShutdown().select().order_by(table.SelfInitShutdown.id.desc()).get()
                            if (datetime.datetime.now() - lastReboot.datetime).seconds <= 300:
                                # C_Action.Reboot()
                                Q_Internal.put(C_Prepare.SelfInitShutdown(getframeinfo(currentframe())[2], 'reboot', datetime.datetime.now()))
                                logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'reboot')
                                break
                            else:
                                Q_Internal.put(C_Prepare.SelfInitShutdown(getframeinfo(currentframe())[2], 'rebootAccessDenied', datetime.datetime.now()))
                                logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'rebootAccessDenied')
                    else:
                        Q_Internal.put(C_Prepare.SelfInitShutdown(getframeinfo(currentframe())[2], 'rebootAccessDenied', datetime.datetime.now()))
                        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'rebootAccessDenied')

            time.sleep(3)