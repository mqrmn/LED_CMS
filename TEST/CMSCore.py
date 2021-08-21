# 1.1.1

import sys
import win32serviceutil
import win32service
import win32event
import servicemanager
import time
import os
import threading
import queue
from inspect import currentframe, getframeinfo

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config
from App import LogManager, Comm, Resource, Handler, Validation, File, Action, Database

logging = LogManager.Log_Manager()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])


module = 'TEST'
def TEST():

        Q_Internal = queue.Queue()
        C_Action = Action.Init()
        C_Action.InitCMS(Q_Internal)

        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')

        # Создаю экземпляры классов
        C_Handlers = Handler.Queue()
        C_Network = Comm.Socket()
        C_File = File.Manager()
        C_Valid = Validation._System_()
        C_DB = Database.DBFoo()
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Экземпляры классов созданы')

        # Очереди
        Q_FromUA = queue.Queue()
        Q_Action = queue.Queue()
        Q_UA_TCPSend = queue.Queue()
        Q_Cont_TCPSend = queue.Queue()
        Q_ValidProc = queue.Queue()
        Q_PrepareToSend = queue.Queue()
        Q_ValidScreen = queue.Queue()
        Q_SetFlag = queue.Queue()
        Q_UAValid = queue.Queue()
        Q_DBWrite = queue.Queue()
        Q_UAValidSF = queue.Queue()

        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Очереди созданы')

        # Потоки
        # Потоки обмена
        T_Server = threading.Thread(target=C_Network.Server, args=(Config.localhost, Config.CMSCoreInternalPort, Q_FromUA))

        T_UA_Client = threading.Thread(target=C_Network.Client, args=(Config.localhost, Config.CMSUserAgentPort, Q_UA_TCPSend))
        T_Contr_Client = threading.Thread(target=C_Network.Client, args=(Config.localhost, Config.CMSControllertPort, Q_Cont_TCPSend))

        # Потоки обработки входящих данных
        TQ_FromUA = threading.Thread(target=C_Handlers.FromUA, args=(Q_FromUA, Q_ValidScreen, Q_ValidProc, Q_Internal))
        TQ_ValidScreen = threading.Thread(target=C_Handlers.Valid, args=(
        Q_ValidScreen, Q_Action, True, 1, Resource.ComDict['head'][0], True,))
        TQ_ValidProc = threading.Thread(target=C_Handlers.Valid, args=(Q_ValidProc, Q_Action, False, 1, Resource.ComDict['head'][0], True,))

        # Потоки формирования исходящих данных
        TQ_CreateAction = threading.Thread(target=C_Handlers.CreateAction, args=(Q_Action, Q_PrepareToSend, Q_SetFlag))
        TQ_SendController = threading.Thread(target=C_Handlers.SendController, args=(Q_PrepareToSend, Q_UA_TCPSend, Q_SetFlag))

        # Потоки обработки внутренних данных
        TQ_Internal = threading.Thread(target=C_Handlers.Internal, args=(Q_Internal, Q_UAValid, Q_DBWrite, Q_SetFlag))
        TQ_SetFlag = threading.Thread(target=C_Handlers.SetFlag, args=(Q_SetFlag, Q_UAValidSF, Q_Cont_TCPSend))

        # Обработка записи в БД
        T_DBWriteController = (threading.Thread(target=C_DB.WriteController, args=(Q_DBWrite,)))

        # Служебные потоки
        T_CheckNewContent = threading.Thread(target=C_File.DynamicRenewCont, args=(Q_PrepareToSend, ))
        TQ_UAValid = threading.Thread(target=C_Valid.UAValid, args=(Q_UAValid, Q_Internal, Q_UAValidSF))

        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Потоки инициализированы')

        # Запуск потоков
        T_Server.start()
        T_UA_Client.start()
        TQ_FromUA.start()
        TQ_CreateAction.start()
        TQ_SendController.start()
        TQ_ValidScreen.start()
        TQ_ValidProc.start()
        T_CheckNewContent.start()
        T_Contr_Client.start()

        TQ_Internal.start()
        TQ_UAValid.start()
        T_DBWriteController.start()
        TQ_SetFlag.start()
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Потоки запущены')

        # Цикл
        # --------------------------------------------------------------------


if __name__ == '__main__':
    TEST()
