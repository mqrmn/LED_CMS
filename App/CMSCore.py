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
        Validation_ = Validation.System()
        File_Manager = FileManager.System()
        Default_ = Restore.Default()


        # Обновляю CMS
        File_Manager.CMSUpgrade()
        # Проверяю NovaStudio
        Validation_.NovaStudio()
        # Обновляю контент
        File_Manager.ContentRenewHandler()

        # Проверяю статус последнего выключения
        Validation_.LastShutdown()
        # Обнуляю временные файлы
        File_Manager.TempDeleter()
        Default_.TempFiles()

        # Чищу логи
        File_Manager.LogArchiever()
        File_Manager.LogDeleter()

        # Удаляю экземпляры классов
        Validation_ = None
        File_Manager = None
        Default_ = None

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
                                        args=(Config.localhost, Config.CMSCoreInternalPort, CMSUserAgentQueue,))                            # Поток внутреннего сокета



        CMSUserAgentQueueHandler = threading.Thread(target=Handlers_.CMSUserAgentQueueHandler,
                                                    args=(CMSUserAgentQueue, ScreenValidationQueue, InternalQueue, ExecutionQueue,))         # Обработчик очереди данных CMSUserAgent


        CoreScreenValidationThread = threading.Thread(target=Validation_.CoreScreenValidation,
                                                      args=(ScreenValidationQueue,ExecutionQueue,))                                          # Поток проверки данных валидатора экран

        # ExecutionThread = threading.Thread(target=Execute_.RestartNovaStudio,
        #                                    args=(ExecutionQueue, SendUserAgentQueue,))

        SendUserAgentThread = threading.Thread(target=Network_.SendUserAgent,
                                               args=(Config.localhost, Config.CMSCoreInternalPort, SendUserAgentQueue,))

        # Запуск потоков
        serverThread.start()
        CMSUserAgentQueueHandler.start()
        CoreScreenValidationThread.start()
        # ExecutionThread.start()



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