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

logging = LogManager.LogManager()
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

        # Инициализация
        # --------------------------------------------------------------------
        # Создаю экземпляры классов
        validation_ = Validation.System()
        file_manager = FileManager.System()
        default_ = Restore.Default()
        handlers_ = Handlers.Handler()
        network_ = Communicate.Network()




        # Обновляю CMS
        file_manager.CMSUpgrade()
        # Проверяю NovaStudio
        validation_.NovaStudio()
        # Обновляю контент
        file_manager.ContentRenewHandler()

        # Проверяю статус последнего выключения
        validation_.LastShutdown()
        # Обнуляю временные файлы
        file_manager.TempDeleter()
        default_.TempFiles()

        # Чищу логи
        file_manager.LogArchiever()
        file_manager.LogDeleter()

        # Удаляю экземпляры классов


        # Очереди
        Q_CMSUserAgent = queue.Queue()
        #InternalQueue = queue.Queue()
        Q_ScreenValidation = queue.Queue()
        Q_Execution = queue.Queue()
        Q_SendUserAgent = queue.Queue()

        # Экземпляры классов


        # Потоки
        T_server = threading.Thread(target=network_.Server,
                                        args=(Config.localhost, Config.CMSCoreInternalPort, Q_CMSUserAgent))  # Поток внутреннего сокета

        TQH_CMSUserAgent = threading.Thread(target=handlers_.CMSUserAgentQueueHandler,
                                                    args=(Q_CMSUserAgent, Q_ScreenValidation))  # Обработчик очереди данных CMSUserAgent

        TQH_CoreScreenValidation = threading.Thread(target=validation_.CoreScreenValidation,
                                                      args=(Q_ScreenValidation, Q_Execution))  # Поток проверки данных валидатора экран

        TQH_Execution = threading.Thread(target=handlers_.ExecutionQueueHandler,
                                           args=(Q_Execution, Q_SendUserAgent))

        T_SendUserAgent = threading.Thread(target=network_.SendUserAgent,
                                               args=(Config.localhost, Config.CMSUserAgentPort, Q_SendUserAgent))

        # Запуск потоков
        T_server.start()
        TQH_CMSUserAgent.start()
        TQH_CoreScreenValidation.start()
        TQH_Execution.start()
        T_SendUserAgent.start()

        validation_ = None
        file_manager = None
        default_ = None


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