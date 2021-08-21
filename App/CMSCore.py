# 1.1.1

import sys
import win32serviceutil
import win32service
import win32event
import servicemanager
import time
import threading
import queue

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config
from App import LogManager, Comm, Resource, Handler, Validation, File, Action, Database

LOG = LogManager.Log_Manager()
LOG.CMSLogger('CALLED')

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

        Q_Internal = queue.Queue()
        C_Action = Action.Init()
        C_Action.InitCMS(Q_Internal)

        LOG.CMSLogger('Called')

        # Создаю экземпляры классов
        C_Handlers = Handler.Queue()
        C_Network = Comm.Socket()
        C_File = File.Manager()
        C_Valid = Validation._System_()
        C_DB = Database.DBFoo()
        LOG.CMSLogger('Экземпляры классов созданы')

        # Очереди
        Q_FromUA = queue.Queue()
        Q_Action = queue.Queue()
        Q_TCPSend = queue.Queue()
        Q_ValidProc = queue.Queue()
        Q_PrepareToSend = queue.Queue()
        Q_ValidScreen = queue.Queue()
        Q_SetFlag = queue.Queue()
        Q_UAValid = queue.Queue()
        Q_DBWrite = queue.Queue()
        Q_UAValidSF = queue.Queue()
        Q_Controller = queue.Queue()

        LOG.CMSLogger('Очереди созданы')

        # Потоки
        # Потоки обмена
        T_Server = threading.Thread(target=C_Network.Server,
                                    args=(Config.localhost, Config.CMSCoreInternalPort, Q_FromUA))

        T_ClientUA = threading.Thread(target=C_Network.Client,
                                      args=(Config.localhost, Config.CMSUserAgentPort, Q_TCPSend))
        T_ClientContr = threading.Thread(target=C_Network.Client,
                                         args=(Config.localhost, Config.CMSControllertPort, Q_TCPSend))

        # Потоки обработки входящих данных
        TQ_FromUA = threading.Thread(target=C_Handlers.FromUA, args=(Q_FromUA, Q_ValidScreen, Q_ValidProc, Q_Internal))
        TQ_ValidScreen = threading.Thread(target=C_Handlers.Valid, args=(
            Q_ValidScreen, Q_Action, True, 1, Resource.ComDict['head'][0], True,))
        TQ_ValidProc = threading.Thread(target=C_Handlers.Valid,
                                        args=(Q_ValidProc, Q_Action, False, 1, Resource.ComDict['head'][0], True,))

        # Потоки формирования исходящих данных
        TQ_CreateAction = threading.Thread(target=C_Handlers.CreateAction, args=(Q_Action, Q_PrepareToSend, Q_SetFlag))
        TQ_SendController = threading.Thread(target=C_Handlers.SendController,
                                             args=(Q_PrepareToSend, Q_TCPSend, Q_SetFlag))

        # Потоки обработки внутренних данных
        TQ_Internal = threading.Thread(target=C_Handlers.Internal, args=(Q_Internal, Q_UAValid, Q_DBWrite, Q_SetFlag))
        TQ_SetFlag = threading.Thread(target=C_Handlers.SetFlag, args=(Q_SetFlag, Q_UAValidSF, Q_Controller))

        # Обработка записи в БД
        T_DBWriteController = (threading.Thread(target=C_DB.WriteController, args=(Q_DBWrite,)))

        # Служебные потоки
        T_CheckNewContent = threading.Thread(target=C_File.DynamicRenewCont, args=(Q_PrepareToSend,))
        TQ_UAValid = threading.Thread(target=C_Valid.UAValid, args=(Q_UAValid, Q_Internal, Q_UAValidSF))

        LOG.CMSLogger( 'Потоки инициализированы')

        # Запуск потоков
        T_Server.start()
        T_ClientUA.start()
        TQ_FromUA.start()
        TQ_CreateAction.start()
        TQ_SendController.start()
        TQ_ValidScreen.start()
        TQ_ValidProc.start()
        T_CheckNewContent.start()

        TQ_Internal.start()
        TQ_UAValid.start()
        T_DBWriteController.start()
        TQ_SetFlag.start()
        LOG.CMSLogger('Потоки запущены')

        # Цикл
        # --------------------------------------------------------------------
        while True:
            # Контроль потоков
            time.sleep(10)

        # Граница цикла
        #----------------------------------------------------------------------

            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            if rc == win32event.WAIT_OBJECT_0:

                LOG.CMSLogger( 'Получена команда на остановку службы')
                C_Comm = Comm.Socket()
                C_Comm.Send(Config.localhost, Config.CMSUserAgentPort, Resource.TerminateThread[0])
                LOG.CMSLogger('Команда на остановку UA отправлена')
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