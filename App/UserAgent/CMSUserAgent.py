# v.1.1.1

from App import Validation
import threading
import queue
from App import Communicate
from App.Config import Config
from App import Handlers
from App import WinApi
from inspect import currentframe, getframeinfo

import logging
import time

module = 'CMSUserAgent'

def main():

    lowScreenStateQueue = queue.Queue()                    # Очередь результатов проверки экрана

    CMSCoreDataQueue = queue.Queue()
    Q_SendCore = queue.Queue()
    Q_ProcState_ = queue.Queue()
    Q_CheckedProcState_ = queue.Queue()

    Validation_ = Validation._System_()                   # Экземпляр класса валидации
    Network_ = Communicate._Network_()                    # Экземпляр класса сервера
    Handlers_ = Handlers._QHandler_()
    network_ = Communicate._Network_()
    _WinApi_ = WinApi._API_()
    _QHandler_ = Handlers._QHandler_()
    _Validation_ = Validation._System_()

    serverThread = threading.Thread(target=Network_.Server, args=(Config.localhost, Config.CMSUserAgentPort, CMSCoreDataQueue,))  # Сокет, принимающий данные от CMSCore

    getScreenValidationTread = threading.Thread(target=Validation_.GetScreenStatic, args=(lowScreenStateQueue,))                # Поток проверки экрана

    checkScreenValidationTread = threading.Thread(target=Handlers_.Validation, args=(lowScreenStateQueue, Q_SendCore, True, 4, 'CheckScreenValidation', True, module,))


    T_GetProcState = threading.Thread(target=_Validation_.GetProcessState, args=(Q_ProcState_,))
    TQH_CheckProcList = threading.Thread(target=_QHandler_.CheckProcList, args=(Q_ProcState_, Q_CheckedProcState_))
    THQ_ValidateProcState = threading.Thread(target=_QHandler_.Validation, args=(Q_CheckedProcState_, Q_SendCore, False, 2, None, True, module,))

    T_NetworkClient = threading.Thread(target=network_.Client, args=(Config.localhost, Config.CMSCoreInternalPort, Q_SendCore))

    CMSCoreDataQueueHandlerThread = threading.Thread(target=Handlers_.FromCore, args=(CMSCoreDataQueue,))


    serverThread.start()
    getScreenValidationTread.start()
    checkScreenValidationTread.start()

    TQH_CheckProcList.start()
    THQ_ValidateProcState.start()
    T_GetProcState.start()

    CMSCoreDataQueueHandlerThread.start()
    T_NetworkClient.start()





