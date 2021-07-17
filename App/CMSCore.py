#v.1.1.1
import sys

sys.path.append("C:\\MOBILE\\Local\\CMS")

import win32serviceutil
import win32service
import win32event
import servicemanager
import time
import os
from App.Config import Config
from App import LogManager, Restore, Validation, FileManager

import threading
from App import Validation, Communicate
from App.Config import Config
from App.UserAgent import CMSUserAgent
import queue
from App import Handlers
from App import Execution

from inspect import currentframe, getframeinfo
import subprocess

logging = LogManager._Log_Manager_()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])



class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "CMS"
    _svc_display_name_ = "CMS"
    _svc_description_ = "Обслуживает систему трансляции контента"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.hWaitResume = win32event.CreateEvent(None, 0, 0, None)
        self.timeout = 10000
        self.resumeTimeout = 1000
        self._paused = False

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STOPPED,
                              (self._svc_name_, ''))

    def SvcPause(self):
        self.ReportServiceStatus(win32service.SERVICE_PAUSE_PENDING)
        self._paused = True
        self.ReportServiceStatus(win32service.SERVICE_PAUSED)
        servicemanager.LogInfoMsg("The %s service has paused." % (self._svc_name_,))

    def SvcContinue(self):
        self.ReportServiceStatus(win32service.SERVICE_CONTINUE_PENDING)
        win32event.SetEvent(self.hWaitResume)
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        servicemanager.LogInfoMsg("The %s service has resumed." % (self._svc_name_,))

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()



    def main(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        module = 'CMSCore'
        # Инициализация
        # --------------------------------------------------------------------
        # Создаю экземпляры классов
        _validation_ = Validation._System_()
        _file_manager_ = FileManager._System_()
        _default_ = Restore._Default_()
        _handlers_ = Handlers._QHandler_()
        _network_ = Communicate._Network_()


        # Обновляю CMS
        _file_manager_.CMSUpgrade()
        # Проверяю NovaStudio
        _validation_.NovaStudio()
        # Обновляю контент
        _file_manager_.ContentRenewHandler()

        # Проверяю статус последнего выключения
        _validation_.LastShutdown()
        # Обнуляю временные файлы
        _file_manager_.TempDeleter()
        _default_.TempFiles()

        # Чищу логи
        _file_manager_.LogArchiever()
        _file_manager_.LogDeleter()

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

        # Потоки
        T_InternalSocket = threading.Thread(target=_network_.Server, args=(Config.localhost, Config.CMSCoreInternalPort, Q_CMSUserAgent_))  # Прием данных от CMSUserAgent
        TQH_CMSUserAgent = threading.Thread(target=_handlers_.FromUserAgent, args=(Q_CMSUserAgent_, Q_ScreenValidation_, Q_procValidation_))  # Обработчик очереди данных от CMSUserAgent
        TQH_ValidationScreen = threading.Thread(target=_handlers_.Validation, args=(Q_ScreenValidation_, Q_Execution_, True, 2, 'CoreScreenValidation', False, module))  # Счетчик кондиции экрана
        THQ_ProcValidation_ = threading.Thread(target=_handlers_.Validation, args=(Q_procValidation_, Q_Execution_, True, 2, 'RunNovaStudio', False, module))
        TQH_Execution = threading.Thread(target=_handlers_.Execution, args=(Q_Execution_, Q_SendUserAgent_))  # Обработчик очереди команд для CMSUserAgent
        T_NetworkClient = threading.Thread(target=_network_.Client, args=(Config.localhost, Config.CMSUserAgentPort, Q_SendUserAgent_))  # Отправка данных на CMSUserAgent

        # Запуск потоков
        T_InternalSocket.start()
        TQH_CMSUserAgent.start()
        TQH_Execution.start()
        T_NetworkClient.start()
        TQH_ValidationScreen.start()
        THQ_ProcValidation_.start()

        _validation_ = None
        _file_manager_ = None
        _default_ = None


        # Цикл проверок
        # --------------------------------------------------------------------
        while True:
            time.sleep(10)

        # Граница цикла
        #----------------------------------------------------------------------

            # Проверяем не поступила ли команда завершения работы службы
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            if rc == win32event.WAIT_OBJECT_0:
                # Здесь выполняем необходимые действия при остановке службы
                servicemanager.LogInfoMsg("Service finished")
                break
            # Здесь выполняем необходимые действия при приостановке службы
            if self._paused:
                servicemanager.LogInfoMsg("Service paused")
            # Приостановка работы службы
            while self._paused:
                # Проверям не поступила ли команда возобновления работы службы
                rc = win32event.WaitForSingleObject(self.hWaitResume, self.resumeTimeout)
                if rc == win32event.WAIT_OBJECT_0:
                    self._paused = False
                    # Здесь выполняем необходимые действия при возобновлении работы службы
                    servicemanager.LogInfoMsg("Service continue")
                    break

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)