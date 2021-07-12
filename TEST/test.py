import logging
import threading
from App import Validation, Communicate
from App.Config import Config
from App.UserAgent import CMSUserAgent
import queue
from App import Handlers
from App import Execution
from inspect import currentframe, getframeinfo

def TEST():
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


    TQH_CMSUserAgent = threading.Thread(target=handlers_.CMSUserAgentQueueHandler, args=(Q_CMSUserAgent, Q_ScreenValidation))  # Обработчик очереди данных от CMSUserAgent






    TQH_ValidationScreen = threading.Thread(target=handlers_.ValidationHandler, args=(Q_ScreenValidation, Q_Execution, True, 4, 'CoreScreenValidation', False, getframeinfo(currentframe())[2]))  # Счетчик кондиции экрана

    TQH_Execution = threading.Thread(target=handlers_.ExecutionQueueHandler,
                                     args=(Q_Execution, Q_SendUserAgent))  # Обработчик очереди команд для CMSUserAgent

    T_NetworkClient = threading.Thread(target=network_.Client, args=(
    Config.localhost, Config.CMSUserAgentPort, Q_SendUserAgent))  # Отправка данных на CMSUserAgent

    # Execution

    # Запуск потоков
    T_InternalSocket.start()
    TQH_CMSUserAgent.start()
    TQH_Execution.start()
    T_NetworkClient.start()
    TQH_ValidationScreen.start()

    CMSUserAgent.main()

    # from App import WinApi
    # meth = WinApi.API()
    # a = meth.CheckProcessNovaStudio()
    # print(a)




if __name__ == '__main__':
    TEST()