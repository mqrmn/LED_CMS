# v.1.1.1

from App import Validation
import threading
import queue
from App import Communicate
from  App.Config import Config
from App import Handlers
import logging
import time

module = 'CMSUserAgent.main'

def main():
    lowScreenStateQueue = queue.Queue()                    # Очередь результатов проверки экрана
    CMSCoreDataQueue = queue.Queue()

    Validation_ = Validation.System()                   # Экземпляр класса валидации
    Network_ = Communicate.Network()                    # Экземпляр класса сервера
    Handlers_ = Handlers.Handler()


    getScreenValidationTread = threading.Thread(target=Validation_.GetScreenValidation, args=(lowScreenStateQueue, ))                # Поток проверки экрана
    checkScreenValidationTread = threading.Thread(target=Validation_.CheckScreenValidation, args=(lowScreenStateQueue, ))            # Счетчик проверки экрана
    serverThread = threading.Thread(target=Network_.Server, args=(Config.localhost, Config.CMSUserAgentPort, CMSCoreDataQueue,))     # Сокет, принимающий данные от CMSCore
    CMSCoreDataQueueHandlerThread = threading.Thread(target=Handlers_.CMSCoreDataQueueHandler,
                                                     args=(CMSCoreDataQueue,))

    serverThread.start()
    getScreenValidationTread.start()
    checkScreenValidationTread.start()
    CMSCoreDataQueueHandlerThread.start()