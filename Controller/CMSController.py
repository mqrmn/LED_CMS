#v.1.1.1

import sys
sys.path.append("C:\\MOBILE\\Local\\CMS")

import win32serviceutil
import win32service
import win32event
import servicemanager
import time
import datetime
import threading
import queue
import socket
import pythoncom
from App import API, File, Action
from App.Config import Config
import os
from App import LogManager, Controller
from inspect import currentframe, getframeinfo
logging = LogManager._Log_Manager_()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])

class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "CMSController"
    _svc_display_name_ = "CMSController"
    _svc_description_ = "CMSController v.1.1.1"

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

        # Создание экзепляров классов
        C_Win = API.Win()
        C_FileMan = File.Manager()
        C_Action = Action.System()
        C_Control = Controller.CMS()

        # Создание очередей
        Q_Internal = queue.Queue()

        # Инициализация потоков
        T_Updater = threading.Thread(target=C_Control.CMSUpdater, args=(Q_Internal,))

        # Запуск потоков
        T_Updater.start()

        # Цикл
        # --------------------------------------------------------------------
        checkTime = datetime.datetime.now()
        while True:
            print((checkTime - datetime.datetime.now()).seconds)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as Socket:
                try:
                    Socket.connect((Config.localhost, Config.CMSCoreInternalPort))
                    checkTime = datetime.datetime.now()
                    logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'СЛУЖБА ЗАПУЩЕНА', )
                except:

                    if Q_Internal.empty() == False:
                        if Q_Internal.get() == True:
                            logging.CMSLogger(logHandler, getframeinfo(currentframe())[2],
                                              'СЛУЖБА ОСТАНОВЛЕНА ВСВЯЗИ С ОБНОВЛЕНИЕМ', )
                            break

                        else:
                            pass
                    else:
                        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'СЛУЖБА ОСТАНОВЛЕНА', )
                        if ((checkTime - datetime.datetime.now()).seconds >= 300):
                            logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'REBOOT')
                            C_Action.Reboot()
                            break

            time.sleep(30)

        # Граница цикла
        #----------------------------------------------------------------------

            # Проверяем не поступила ли команда завершения работы службы
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            if rc == win32event.WAIT_OBJECT_0:
                # Здесь выполняем необходимые действия при остановке службы
                pythoncom.CoInitialize()
                stSvc = C_Win.StopService('CMS')
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