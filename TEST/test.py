import logging
import queue
import threading
import time
from multiprocessing import Process

from App import Validation
from App import WinApi
from App import Handlers
from App import Handlers, Communicate
from App.Config import Config
from  App.UserAgent import CMSUserAgent
from App import Resource


module = 'TEST'
def TEST():




    _validation_ = Validation._System_()
    _handlers_ = Handlers._QHandler_()
    _network_ = Communicate._Network_()

    # Простые очереди
    Q_ScreenValidation_ = queue.Queue()

    # Очереди
    Q_CMSUserAgent_ = queue.Queue()
    Q_Execution_ = queue.Queue()
    Q_SendUserAgent_ = queue.Queue()
    Q_procValidation_ = queue.Queue()
    Q_PrepareToSend_ = queue.Queue()

    # Потоки
    T_InternalSocket = threading.Thread(target=_network_.Server, args=(Config.localhost, Config.CMSCoreInternalPort, Q_CMSUserAgent_))                                  # Прием данных от CMSUserAgent
    TQH_CMSUserAgent = threading.Thread(target=_handlers_.FromUserAgent, args=(Q_CMSUserAgent_, Q_ScreenValidation_, Q_procValidation_))                                # Обработчик очереди данных от CMSUserAgent

    TQH_ValidationScreen = threading.Thread(target=_handlers_.Validation, args=(Q_ScreenValidation_, Q_Execution_, True, 2, 'State', False, module))     # Счетчик кондиции экрана
    THQ_ProcValidation_ = threading.Thread(target=_handlers_.Validation_2, args=(Q_procValidation_, Q_Execution_, False, 2, 'State', True, module))
    TQH_Execution = threading.Thread(target=_handlers_.Execution, args=(Q_Execution_, Q_PrepareToSend_))                                                                # Обработчик очереди команд для CMSUserAgent

    # T_PrepareToSend = threading.Thread(target=_handlers_.PrepareToSend, args=(Q_SendUserAgent_, Q_SendCore,))
    # T_NetworkClient = threading.Thread(target=_network_.Client, args=(Config.localhost, Config.CMSUserAgentPort, Q_SendUserAgent_))                                     # Отправка данных на CMSUserAgent

    # Запуск потоков
    T_InternalSocket.start()
    TQH_CMSUserAgent.start()
    TQH_Execution.start()
    # T_NetworkClient.start()
    TQH_ValidationScreen.start()
    THQ_ProcValidation_.start()



    CMSUserAgent.main()




if __name__ == '__main__':
    TEST()