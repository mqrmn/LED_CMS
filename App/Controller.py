# 1.1.1

import sys
import time
import pythoncom
import datetime
import numpy as np
import pyautogui
import cv2
import random
import threading
from inspect import currentframe, getframeinfo

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config
from App import Validation, Resource, File, API, Action, LogManager, Database

LOG = LogManager.Log_Manager()


class CMS:
    def Thread(self, Q_in, Q_out, data):
        while True:
            if Q_in.empty() == False:
                Q_data = Q_in.get()
                if Q_data == Resource.TerminateThread[0]:
                    break
            C_Valid = Validation.System()
            Th_States = C_Valid.Threads(data)
            if False in Th_States:
                pass
            time.sleep(10)

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

                if ((datetime.datetime.now() - data).seconds) >= 300:


                    pythoncom.CoInitialize()

                    if FLAG > 0:
                        if FLAG > 1:
                            C_Action.RebootInit()
                            Q_Internal.put(C_Prepare.SelfInitShutdown(getframeinfo(currentframe())[2], 'reboot', datetime.datetime.now()))
                            LOG.CMSLogger('reboot')
                            break
                        else:
                            lastReboot = table.SelfInitShutdown().select().order_by(table.SelfInitShutdown.id.desc()).get()
                            if (datetime.datetime.now() - lastReboot.datetime).seconds <= 300:
                                C_Action.RebootInit()
                                Q_Internal.put(C_Prepare.SelfInitShutdown(getframeinfo(currentframe())[2], 'reboot', datetime.datetime.now()))
                                LOG.CMSLogger('reboot')
                                break
                            else:
                                Q_Internal.put(C_Prepare.SelfInitShutdown(getframeinfo(currentframe())[2], 'rebootAccessDenied', datetime.datetime.now()))
                                LOG.CMSLogger('rebootAccessDenied')
                    else:
                        Q_Internal.put(C_Prepare.SelfInitShutdown(getframeinfo(currentframe())[2], 'rebootAccessDenied', datetime.datetime.now()))
                        LOG.CMSLogger('rebootAccessDenied')

            time.sleep(3)

    def GetScreenStatic(self, screenStateQueue):
        chanelSumArr = []
        if Config.screenNum == 1:  # По количеству областей будет допиливаться
            while True:
                while len(chanelSumArr) < 2:
                    screenShot = pyautogui.screenshot(region=(Config.regiondict[0]))  # Снимок экрана
                    chanelIntens = cv2.cvtColor(np.array(screenShot),
                                                cv2.COLOR_RGB2BGR)  # передача изображения на анализ каналов
                    commonIntens = chanelIntens.sum(axis=2)  # посмотреть что делает эта строка
                    chanelSum = np.sum(commonIntens)  # Сумма интенсивности по каналам
                    if len(chanelSumArr) < 2:
                        chanelSumArr.append(chanelSum)

                # Проверка значений, передача результата в очередь
                if len(chanelSumArr) == 2:
                    if (chanelSumArr[0] == chanelSumArr[1]):  # Экран статичен
                        screenStateQueue.put({'key': Resource.ComDict['key'][0],
                                              'data': [Resource.ComDict['data'][Resource.ComDict['key'][0]][0],
                                                       True], })
                    else:
                        screenStateQueue.put({'key': Resource.ComDict['key'][0],
                                              'data': [Resource.ComDict['data'][Resource.ComDict['key'][0]][0],
                                                       False], })
                    del chanelSumArr[0]  # Удаляю из словаря запись с индексом 0
                time.sleep(random.randint(Config.timeoutSCheck[0], Config.timeoutSCheck[1]))
        else:
            pass

    def GetProcessState(self, Q_ProcState):
        C_WinApi = API.Process()
        while True:
            T_GetProcessState = threading.Thread(target=C_WinApi.GetProcessState, args=(Q_ProcState,))
            T_GetProcessState.start()
            T_GetProcessState.join()
            time.sleep(Config.timeoutPCheck)