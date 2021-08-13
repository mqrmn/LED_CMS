# 1.1.1

import sys
import win32serviceutil
import win32service
import win32event
import servicemanager
import time
import os
import threading
import queue
from inspect import currentframe, getframeinfo

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config
from App import LogManager, Comm, Resource, Handler, Validation, File

logging = LogManager._Log_Manager_()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])

class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "CMS"
    _svc_display_name_ = "CMS"
    _svc_description_ = "CMS"

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
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')

        # Создаю экземпляры классов
        C_Handlers = Handler.Queue()
        C_Network = Comm.Socket()
        C_File = File.Manager()
        C_Valid = Validation._System_()
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Экземпляры классов созданы')

        # Очереди
        Q_FromUA = queue.Queue()
        Q_Action = queue.Queue()
        Q_Send = queue.Queue()
        Q_ValidProc = queue.Queue()
        Q_PrepareToSend = queue.Queue()
        Q_ValidScreen = queue.Queue()
        Q_Internal = queue.Queue()
        Q_UAValid = queue.Queue()
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Очереди созданы')

        # Потоки
        T_Server = threading.Thread(target=C_Network.Server, args=(Config.localhost, Config.CMSCoreInternalPort, Q_FromUA))     # Прием данных TCP
        T_Client = threading.Thread(target=C_Network.Client, args=(Config.localhost, Config.CMSUserAgentPort, Q_Send))          # Отправка данных TCP
        TQ_FromUA = threading.Thread(target=C_Handlers.FromUA, args=(Q_FromUA, Q_ValidScreen, Q_ValidProc, Q_Internal))              # Обработчик очереди данных от CMSUserAgent
        TQ_CreateAction = threading.Thread(target=C_Handlers.CreateAction, args=(Q_Action, Q_PrepareToSend))                       # Обработчик очереди команд для CMSUserAgent
        TQ_PrepareToSend = threading.Thread(target=C_Handlers.SendController, args=(Q_PrepareToSend, Q_Send,))
        TQ_ValidScreen = threading.Thread(target=C_Handlers.Valid, args=(Q_ValidScreen, Q_Action, True, 1, Resource.ComDict['head'][0], True,))  # Счетчик кондиции экрана
        TQ_ValidProc = threading.Thread(target=C_Handlers.Valid, args=(Q_ValidProc, Q_Action, False, 1, Resource.ComDict['head'][0], True,))
        T_CheckNewContent = threading.Thread(target=C_File.DynamicRenewCont, args=(Q_PrepareToSend,))

        TQ_Internal = threading.Thread(target=C_Handlers.Internal, args=(Q_Internal, Q_UAValid,))
        TQ_UAValid = threading.Thread(target=C_Valid.UAValid, args=(Q_UAValid,))

        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Потоки инициализированы')

        # Запуск потоков
        T_Server.start()
        T_Client.start()
        TQ_FromUA.start()
        TQ_CreateAction.start()
        TQ_PrepareToSend.start()
        TQ_ValidScreen.start()
        TQ_ValidProc.start()
        T_CheckNewContent.start()

        TQ_Internal.start()
        TQ_UAValid.start()
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Потоки запущены')
        # Цикл
        # --------------------------------------------------------------------
        while True:
            # Контроль потоков
            time.sleep(10)

        # Граница цикла
        #----------------------------------------------------------------------

            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            if rc == win32event.WAIT_OBJECT_0:

                logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Получена команда на остановку службы')
                C_Comm = Comm.Socket()
                C_Comm.Send(Config.localhost, Config.CMSUserAgentPort, Resource.TerminateThread[0])
                logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Команда на остановку UA отправлена')
                servicemanager.LogInfoMsg("Service finished")
                break

            if self._paused:
                servicemanager.LogInfoMsg("Service paused")
            while self._paused:
                rc = win32event.WaitForSingleObject(self.hWaitResume, self.resumeTimeout)
                if rc == win32event.WAIT_OBJECT_0:
                    self._paused = False
                    servicemanager.LogInfoMsg("Service continue")
                    break

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)