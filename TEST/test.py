import logging
import threading
from App import Validation, Communicate
from App.Config import Config
from App.UserAgent import CMSUserAgent
import queue
from App import Handlers
from App import Execution

def main():
    # Очереди
    CMSUserAgentQueue = queue.Queue()
    InternalQueue = queue.Queue()
    ScreenValidationQueue = queue.Queue()
    ExecutionQueue = queue.Queue()
    SendUserAgentQueue = queue.Queue()

    # Экземпляры классов
    Handlers_ = Handlers.Handler()
    Network_ = Communicate.Network()  # Сокет, принимающий данные от CMSUserAgent
    Validation_ = Validation.System()
    Execute_ = Execution.Execute()

    # Потоки
    serverThread = threading.Thread(target=Network_.Server,
                                    args=(Config.localhost, Config.CMSCoreInternalPort,
                                          CMSUserAgentQueue))  # Поток внутреннего сокета

    CMSUserAgentQueueHandler = threading.Thread(target=Handlers_.CMSUserAgentQueueHandler,
                                                args=(CMSUserAgentQueue, ScreenValidationQueue))  # Обработчик очереди данных CMSUserAgent

    CoreScreenValidationThread = threading.Thread(target=Validation_.CoreScreenValidation,
                                                  args=(ScreenValidationQueue,
                                                        ExecutionQueue))  # Поток проверки данных валидатора экран

    ExecutionThread = threading.Thread(target=Handlers_.ExecutionQueueHandler,
                                       args=(ExecutionQueue, SendUserAgentQueue))

    SendUserAgentThread = threading.Thread(target=Network_.SendUserAgent,
                                           args=(Config.localhost, Config.CMSUserAgentPort, SendUserAgentQueue))

    # Запуск потоков
    serverThread.start()
    CMSUserAgentQueueHandler.start()
    CoreScreenValidationThread.start()
    ExecutionThread.start()
    SendUserAgentThread.start()

    # While TEST
    CMSUserAgent.main()




if __name__ == '__main__':
    main()