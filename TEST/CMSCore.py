import logging
import queue
import threading
import time
from multiprocessing import Process
import win32serviceutil
import win32service
import win32event
import servicemanager

from App import Validation
from App import WinApi
from App import Handler
from App import Handler, Comm
from App.Config import Config
from  App.UserAgent import CMSUserAgent
from App import Resource, CMSCore, File


module = 'TEST'
def TEST():

        # Создаю экземпляры классов
        C_Handlers = Handler.Queue()
        C_Network = Comm.Socket()
        C_File = File.Manager()
        C_Valid = Validation._System_()
        # Обновление CMS

        # Очереди
        Q_FromUA = queue.Queue()
        Q_Action = queue.Queue()
        Q_Send = queue.Queue()
        Q_ValidProc = queue.Queue()
        Q_PrepareToSend = queue.Queue()
        Q_ValidScreen = queue.Queue()
        Q_Internal = queue.Queue()
        Q_UAValid = queue.Queue()

        # Потоки
        T_Server = threading.Thread(target=C_Network.Server, args=(Config.localhost, Config.CMSCoreInternalPort, Q_FromUA, ))     # Прием данных TCP
        T_Client = threading.Thread(target=C_Network.Client, args=(Config.localhost, Config.CMSUserAgentPort, Q_Send, ))          # Отправка данных TCP
        TQ_FromUA = threading.Thread(target=C_Handlers.FromUA, args=(Q_FromUA, Q_ValidScreen, Q_ValidProc, Q_Internal, ))              # Обработчик очереди данных от CMSUserAgent
        TQ_CreateAction = threading.Thread(target=C_Handlers.CreateAction, args=(Q_Action, Q_PrepareToSend, ))                       # Обработчик очереди команд для CMSUserAgent
        TQ_PrepareToSend = threading.Thread(target=C_Handlers.SendController, args=(Q_PrepareToSend, Q_Send, ))
        TQ_ValidScreen = threading.Thread(target=C_Handlers.Valid, args=(Q_ValidScreen, Q_Action, True, 1, Resource.ComDict['head'][0], True, ))  # Счетчик кондиции экрана
        TQ_ValidProc = threading.Thread(target=C_Handlers.Valid, args=(Q_ValidProc, Q_Action, False, 1, Resource.ComDict['head'][0], True, ))
        T_CheckNewContent = threading.Thread(target=C_File.DynamicRenewCont, args=(Q_PrepareToSend, ))


        TQ_Internal = threading.Thread(target=C_Handlers.Internal, args=(Q_Internal, Q_UAValid, ))
        TQ_UAValid = threading.Thread(target=C_Valid.UAValid, args=(Q_UAValid, ))

        # Запуск потоков
        T_Server.start()
        T_Client.start()
        TQ_FromUA.start()
        TQ_CreateAction.start()
        TQ_PrepareToSend.start()
        TQ_ValidScreen.start()
        TQ_ValidProc.start()
        T_CheckNewContent.start()

        TQ_Internal.start()
        TQ_UAValid.start()

        # Цикл
        # --------------------------------------------------------------------


if __name__ == '__main__':
    TEST()