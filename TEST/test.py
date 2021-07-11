import logging
import threading
from App import Validation, Communicate
from App.Config import Config
from App.UserAgent import CMSUserAgent
import queue
from App import Handlers
from App import Execution

def main():
    handlers_ = Handlers.Handler()
    network_ = Communicate.Network()

    # Очереди
    Q_CMSUserAgent = queue.Queue()
    # InternalQueue = queue.Queue()
    Q_Execution = queue.Queue()
    Q_SendUserAgent = queue.Queue()

    Q_ScreenValidation = queue.Queue()

    # Потоки
    T_InternalSocket = threading.Thread(target=network_.Server, args=(
    Config.localhost, Config.CMSCoreInternalPort, Q_CMSUserAgent))  # Прием данных от CMSUserAgent

    TQH_CMSUserAgent = threading.Thread(target=handlers_.CMSUserAgentQueueHandler, args=(
    Q_CMSUserAgent, Q_ScreenValidation))  # Обработчик очереди данных от CMSUserAgent

    TQH_Execution = threading.Thread(target=handlers_.ExecutionQueueHandler,
                                     args=(Q_Execution, Q_SendUserAgent))  # Обработчик очереди команд для CMSUserAgent

    T_SendUserAgent = threading.Thread(target=network_.Client, args=(
    Config.localhost, Config.CMSUserAgentPort, Q_SendUserAgent))  # Отправка данных на CMSUserAgent

    TQH_ValidationScreen = threading.Thread(target=handlers_.ValidationHandler, args=(
    Q_ScreenValidation, Q_Execution, '0', 2, 'CoreScreenValidation'))  # Счетчик кондиции экрана

    # Запуск потоков
    T_InternalSocket.start()
    TQH_CMSUserAgent.start()
    TQH_Execution.start()
    T_SendUserAgent.start()

    TQH_ValidationScreen.start()

    CMSUserAgent.main()

    # from App import WinApi
    # meth = WinApi.API()
    # a = meth.CheckProcessNovaStudio()
    # print(a)




if __name__ == '__main__':
    main()