# 1.1.1

import sys
import pythoncom
import numpy as np
import pyautogui
import cv2
import random
import time
import datetime
import threading
import socket
from inspect import currentframe, getframeinfo

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config
from App import Valid, API, Act, Log, Database
from App import Resource as R






LOG = Log.Log_Manager()

class Init:
    def __init__(self):
        global o_CrMsg
        o_CrMsg = R.CreateMessage()


class CMS(Init):
    def Thread(self, Q_in, Q_out, data):
        while True:
            if Q_in.empty() == False:
                Q_data = Q_in.get()
                if Q_data == R.TerminateThread[0]:
                    break
            C_Valid = Valid.System()
            Th_States = C_Valid.Threads(data)
            if False in Th_States:
                pass
            time.sleep(10)
    # Tracking UA status
    def UAValid(self, Q_in, Q_Internal):

        C_Prepare = Database.Prepare()
        data = datetime.datetime.now()
        count = 0
        while True:
            if Q_in.empty() == False:
                data = Q_in.get()
                if count == 0:
                    Q_Internal.put(C_Prepare.SystemInitPrep(datetime.datetime.now()))
                    count += 1
            else:
                if ((datetime.datetime.now() - data).seconds) >= 300:
                    Q_Internal.put(o_CrMsg.RebootSystem())

            time.sleep(3)
    # Checking the screen for static
    def GetScreenStatic(self, screenStateQueue):
        chanelSumArr = []
        if Config.screenNum == 1:
            while True:
                while len(chanelSumArr) < 2:
                    screenShot = pyautogui.screenshot(region=(Config.regiondict[0]))
                    chanelIntens = cv2.cvtColor(np.array(screenShot),
                                                cv2.COLOR_RGB2BGR)
                    commonIntens = chanelIntens.sum(axis=2)
                    chanelSum = np.sum(commonIntens)
                    if len(chanelSumArr) < 2:
                        chanelSumArr.append(chanelSum)

                # Checking values, passing the result to the queue
                if len(chanelSumArr) == 2:
                    if (chanelSumArr[0] == chanelSumArr[1]):  # Screen is static
                        screenStateQueue.put({R.r[2]: R.K[0],
                                              R.r[3]: [R.ScreenState[0], True], })
                    else:
                        screenStateQueue.put({R.r[2]: R.K[0],
                                              R.r[3]: [R.ScreenState[0],  False], })
                    del chanelSumArr[0]  # Remove entry with index 0 from the dictionary
                time.sleep(random.randint(Config.timeoutSCheck[0], Config.timeoutSCheck[1]))
        else:
            pass

    # Checking the status of selected processes
    def GetProcessState(self, Q_ProcState):
        C_WinApi = API.Process()
        while True:
            T_GetProcessState = threading.Thread(target=C_WinApi.GetProcessState, args=(Q_ProcState,))
            T_GetProcessState.start()
            T_GetProcessState.join()
            time.sleep(Config.timeoutPCheck)

    def CMSService(self, Q_Manage, Q_FromUpdater, q_internal):
        C_ActionSys = Act.System()
        C_ActionInit = Act.SysInit()
        table = Database.Tables()
        FLAG = C_ActionInit.CheckLastSelfInitStd(Q_Manage)

        while True:
            time.sleep(60)
            if Q_Manage.empty() == False:
                FLAG = Q_Manage.get()[R.r[3]]

                LOG.CMSLogger('Reboot control flag: {}'.format(FLAG))

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as Socket:
                try:
                    Socket.connect((Config.localhost, Config.CMSCoreInternalPort))
                    LOG.CMSLogger('CMS Runned', )
                except:
                    if Q_FromUpdater.empty() == False:
                        if Q_FromUpdater.get() == True:
                            LOG.CMSLogger('CMS Stopped for upgrade', )
                            break
                        else:
                            pass
                    else:
                        LOG.CMSLogger('CMS Stopped', )
                        if FLAG > 0:
                            if FLAG > 1:


                                LOG.CMSLogger('Reboot scheduled')
                                C_ActionSys.RebootInit()

                                break
                            else:

                                lastReboot = table.SelfInitShutdown().select().order_by(
                                    table.SelfInitShutdown.id.desc()).get()
                                if (datetime.datetime.now() - lastReboot.datetime).seconds >= 300:


                                    LOG.CMSLogger('Reboot scheduled')
                                    C_ActionSys.RebootInit()
                                    break
                                else:
                                    LOG.CMSLogger('Restart access denied')
                        else:
                            LOG.CMSLogger('Restart access denied')



    def PowerManager(self, q_PowerManager, Q_Internal, q_PowerManageFlag):

        C_Action = Act.System()

        C_Prepare = Database.Prepare()
        table = Database.Tables()
        while True:
            FLAG = q_PowerManageFlag.get()
            LOG.CMSLogger('Reboot control flag: {}'.format(FLAG))
            data = q_PowerManager.get()
            LOG.CMSLogger('Power manager received data: {}'.format(data))

            if data:

                if FLAG > 0:
                    if FLAG > 1:

                        Q_Internal.put(C_Prepare.SelfInitShutdownPrep(getframeinfo(currentframe())[2], 'reboot',
                                                                      datetime.datetime.now()))
                        LOG.CMSLogger('Reboot scheduled')
                        C_Action.RebootInit()
                        break
                    else:
                        lastReboot = table.SelfInitShutdown().select().order_by(table.SelfInitShutdown.id.desc()).get()
                        if (datetime.datetime.now() - lastReboot.datetime).seconds <= 300:

                            Q_Internal.put(C_Prepare.SelfInitShutdownPrep(getframeinfo(currentframe())[2], 'reboot',
                                                                          datetime.datetime.now()))
                            LOG.CMSLogger('Reboot scheduled')
                            C_Action.RebootInit()
                            break
                        else:
                            Q_Internal.put(
                                C_Prepare.SelfInitShutdownPrep(getframeinfo(currentframe())[2], 'rebootAccessDenied',
                                                               datetime.datetime.now()))
                            LOG.CMSLogger('Restart access denied')
                else:
                    Q_Internal.put(C_Prepare.SelfInitShutdownPrep(getframeinfo(currentframe())[2], 'rebootAccessDenied',
                                                                  datetime.datetime.now()))
                    LOG.CMSLogger('Restart access denied')
            else:
                pass