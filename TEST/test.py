import logging
import threading
import time
from App import Validation, Communicate
from App.Config import Config
from App.UserAgent import CMSUserAgent
import queue
from App import Handlers

def main():
    # Очереди
    CMSUserAgentQueue = queue.Queue()
    ScreenValidationQueue = queue.Queue()

    # Экземпляры классов
    Handlers_ = Handlers.Handler()
    Network_ = Communicate.Network() # Сокет, принимающий данные от CMSUserAgent
    Validation_ = Validation.System()

    # Потоки
    serverThread = threading.Thread(target=Network_.Server, args=(Config.localhost, Config.CMSCoreInternalPort, CMSUserAgentQueue,))
    CMSUserAgentQueueHandler = threading.Thread(target=Handlers_.CMSUserAgentQueueHandler, args=(CMSUserAgentQueue, ScreenValidationQueue,))
    CoreScreenValidationThread = threading.Thread(target=Validation_.CoreScreenValidation, args=(ScreenValidationQueue,))

    # Запуск потоков
    serverThread.start()
    CMSUserAgentQueueHandler.start()
    CoreScreenValidationThread.start()

    # While TEST
    CMSUserAgent.main()




if __name__ == '__main__':
    main()