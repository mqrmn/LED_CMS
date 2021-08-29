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
from App import Log, Comm, Resource, Handler, File, Act, Database, Control, Notify
from App import Resource as R

LOG = Log.Log_Manager()
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

        # Core initialization
        Q_Internal = queue.Queue()
        C_Action = Act.SysInit()

        try:
            C_Action.InitCMS(Q_Internal)
            LOG.CMSLogger('Core initialized')
        except:
            LOG.CMSLogger('Core initialization failed')

        C_Handlers = Handler.Queue()
        C_Network = Comm.Socket()
        C_RenewCont = File.RenewContent()
        C_Valid = Control.CMS()
        C_DB = Database.DBFoo()
        O_SendMailCont = Notify.Mail()

        LOG.CMSLogger('Instances of classes created')

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
        Q_SendMail = queue.Queue()

        LOG.CMSLogger('Queues created')


        # Exchange threads
        T_Server = threading.Thread(target=C_Network.Server,
                                    args=(Config.localhost, Config.CMSCoreInternalPort, Q_FromUA))

        T_ClientUA = threading.Thread(target=C_Network.Client,
                                      args=(Config.localhost, Config.CMSUserAgentPort, Q_TCPSend))
        # T_ClientContr = threading.Thread(target=C_Network.Client,
        #                                  args=(Config.localhost, Config.CMSControllertPort, Q_TCPSend))
        # Inbound processing flows
        T_ReceiveDataFromUA = threading.Thread(target=C_Handlers.FromUA,
                                               args=(Q_FromUA, Q_ValidScreen, Q_ValidProc, Q_Internal))
        T_ValidDataScreen = threading.Thread(target=C_Handlers.Valid,
                                             args=(Q_ValidScreen, Q_Action, True, 1, R.H[0], True))
        T_ValidDataProc = threading.Thread(target=C_Handlers.Valid,
                                           args=(Q_ValidProc, Q_Action, False, 1, R.H[0], True))
        # Outbound shaping streams
        T_CreateAction = threading.Thread(target=C_Handlers.CreateAction,
                                          args=(Q_Action, Q_PrepareToSend, Q_SetFlag))
        T_SendController = threading.Thread(target=C_Handlers.SendController,
                                            args=(Q_PrepareToSend, Q_TCPSend, Q_SetFlag))
        # Internal processing flows
        T_Internal = threading.Thread(target=C_Handlers.Internal,
                                      args=(Q_Internal, Q_UAValid, Q_DBWrite, Q_SetFlag, Q_SendMail))
        T_SetFlag = threading.Thread(target=C_Handlers.SetFlag,
                                     args=(Q_SetFlag, Q_UAValidSF, Q_Controller))

        # Database write processing
        T_DBWriteController = (threading.Thread(target=C_DB.WriteController,
                                                args=(Q_DBWrite, )))
        # Service Streams
        T_CheckNewContent = threading.Thread(target=C_RenewCont.DynamicRenewCont,
                                             args=(Q_PrepareToSend, Q_Internal))
        T_UAValid = threading.Thread(target=C_Valid.UAValid,
                                     args=(Q_UAValid, Q_Internal, Q_UAValidSF))
        T_SendMailCont = threading.Thread(target=O_SendMailCont.SendMailController,
                                          args=(Q_SendMail, ))

        LOG.CMSLogger('Threads are initialized')

        T_Server.start()
        T_ClientUA.start()
        T_ReceiveDataFromUA.start()
        T_CreateAction.start()
        T_SendController.start()
        T_ValidDataScreen.start()
        T_ValidDataProc.start()
        T_CheckNewContent.start()

        T_Internal.start()
        T_UAValid.start()
        T_DBWriteController.start()
        T_SetFlag.start()
        T_SendMailCont.start()

        LOG.CMSLogger('Threads started')


        while True:
            time.sleep(10)

            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            if rc == win32event.WAIT_OBJECT_0:

                LOG.CMSLogger( 'Command to stop service received')
                C_Comm = Comm.Socket()
                C_Comm.Send(Config.localhost, Config.CMSUserAgentPort, R.TerminateThread[0])
                LOG.CMSLogger('UA stop command sent')
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