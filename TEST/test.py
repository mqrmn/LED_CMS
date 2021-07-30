import logging
import queue
import threading
import time
from multiprocessing import Process

from App import Validation
from App import WinApi
from App import Handler
from App import Handler, Comm
from App.Config import Config
from  App.UserAgent import CMSUserAgent
from App import Resource


module = 'TEST'
def TEST():
    # # Создаю экземпляры классов
    # C_Handlers = Handler.Queue()
    # C_Network = Comm.Socket()
    #
    # # Очереди
    # Q_FromUA = queue.Queue()
    # Q_Action = queue.Queue()
    # Q_Send = queue.Queue()
    # Q_ValidProc = queue.Queue()
    # Q_PrepareToSend = queue.Queue()
    # Q_ValidScreen = queue.Queue()
    #
    # # Потоки
    # T_Server = threading.Thread(target=C_Network.Server,
    #                             args=(Config.localhost, Config.CMSCoreInternalPort, Q_FromUA))  # Прием данных TCP
    # T_Client = threading.Thread(target=C_Network.Client,
    #                             args=(Config.localhost, Config.CMSUserAgentPort, Q_Send))  # Отправка данных TCP
    # TQ_FromUA = threading.Thread(target=C_Handlers.FromUA, args=(
    # Q_FromUA, Q_ValidScreen, Q_ValidProc))  # Обработчик очереди данных от CMSUserAgent
    # TQ_CreateAction = threading.Thread(target=C_Handlers.CreateAction,
    #                                    args=(Q_Action, Q_PrepareToSend))  # Обработчик очереди команд для CMSUserAgent
    # TQ_PrepareToSend = threading.Thread(target=C_Handlers.PrepareToSend, args=(Q_PrepareToSend, Q_Send,))
    # TQ_ValidScreen = threading.Thread(target=C_Handlers.Valid, args=(
    # Q_ValidScreen, Q_Action, True, 2, Resource.ComDict['head'][0], True, ))  # Счетчик кондиции экрана
    # TQ_ValidProc = threading.Thread(target=C_Handlers.Valid,
    #                                 args=(Q_ValidProc, Q_Action, False, 2, Resource.ComDict['head'][0], True, ))
    #
    # # Запуск потоков
    # T_Server.start()
    # T_Client.start()
    # TQ_FromUA.start()
    # TQ_CreateAction.start()
    # TQ_PrepareToSend.start()
    # TQ_ValidScreen.start()
    # TQ_ValidProc.start()
    #
    #
    #
    # CMSUserAgent.main()

    x = WinApi.Process()
    # x.StartService('CMS')

    x.StopService('CMS')
    # print(x.StartService())



if __name__ == '__main__':
    TEST()