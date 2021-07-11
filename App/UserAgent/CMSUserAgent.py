# v.1.1.1

from App import Validation
import threading
import queue
from App import Communicate
from App.Config import Config
from App import Handlers

import logging
import time

module = 'CMSUserAgent.main'

def main():
    lowScreenStateQueue = queue.Queue()                    # Очередь результатов проверки экрана
    CMSCoreDataQueue = queue.Queue()
    Q_SendCore = queue.Queue()

    Validation_ = Validation.System()                   # Экземпляр класса валидации
    Network_ = Communicate.Network()                    # Экземпляр класса сервера
    Handlers_ = Handlers.Handler()
    network_ = Communicate.Network()


    getScreenValidationTread = threading.Thread(target=Validation_.GetScreenStatic, args=(lowScreenStateQueue,))                # Поток проверки экрана

    checkScreenValidationTread = threading.Thread(target=Handlers_.ValidationHandler, args=(lowScreenStateQueue, Q_SendCore, True, 2, 'CheckScreenValidation'))

    # checkScreenValidationTread = threading.Thread(target=Validation_.CheckScreenStatic, args=(lowScreenStateQueue, Q_SendCore))            # Счетчик проверки экрана

    #checkProcess = threading.Thread(target=, args=)
    serverThread = threading.Thread(target=Network_.Server, args=(Config.localhost, Config.CMSUserAgentPort, CMSCoreDataQueue,))     # Сокет, принимающий данные от CMSCore

    T_NetworkClient = threading.Thread(target=network_.Client,
                                       args=(Config.localhost, Config.CMSCoreInternalPort, Q_SendCore))

    CMSCoreDataQueueHandlerThread = threading.Thread(target=Handlers_.CMSCoreDataQueueHandler,
                                                     args=(CMSCoreDataQueue,))

    serverThread.start()
    getScreenValidationTread.start()
    checkScreenValidationTread.start()
    CMSCoreDataQueueHandlerThread.start()
    T_NetworkClient.start()




