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

        o_Action = Act.SysInit()
        o_Handlers = Handler.Queue()
        o_Network = Comm.Socket()
        o_RenewCont = File.RenewContent()
        o_Valid = Control.CMS()
        o_DB = Database.DBFoo()
        o_SendMailCont = Notify.Mail()

        LOG.CMSLogger('Instances of classes created')

        q_Internal = queue.Queue()
        q_FromUA = queue.Queue()
        q_Action = queue.Queue()
        q_TCPSend = queue.Queue()
        q_ValidProc = queue.Queue()
        q_PrepareToSend = queue.Queue()
        q_ValidScreen = queue.Queue()
        q_SetFlag = queue.Queue()
        q_UAValid = queue.Queue()
        q_DBWrite = queue.Queue()
        q_UAValidSF = queue.Queue()
        q_Controller = queue.Queue()
        q_SendMail = queue.Queue()
        q_PowerManagerFLAG = queue.Queue()
        q_PowerManager = queue.Queue()

        LOG.CMSLogger('Queues created')

        t_Init = threading.Thread(target=o_Action.InitCMS,
                                  args=(q_Internal,))
        # Exchange threads
        t_Server = threading.Thread(target=o_Network.Server,
                                    args=(Config.localhost, Config.CMSCoreInternalPort, q_FromUA))
        t_ClientUA = threading.Thread(target=o_Network.Client,
                                      args=(Config.localhost, Config.CMSUserAgentPort, q_TCPSend))
        t_ClientContr = threading.Thread(target=o_Network.Client,
                                         args=(Config.localhost, Config.CMSControllertPort, q_TCPSend))

        # Inbound processing flows
        t_ReceiveDataFromUA = threading.Thread(target=o_Handlers.FromUA,
                                               args=(q_FromUA, q_ValidScreen, q_ValidProc, q_Internal))
        t_ValidDataScreen = threading.Thread(target=o_Handlers.Valid,
                                             args=(q_ValidScreen, q_Action, True, 1, R.H[0], True))
        t_ValidDataProc = threading.Thread(target=o_Handlers.Valid,
                                           args=(q_ValidProc, q_Action, False, 1, R.H[0], True))

        # Internal processing flows
        t_Internal = threading.Thread(target=o_Handlers.Internal,
                                      args=(q_Internal, q_UAValid, q_DBWrite, q_SetFlag, q_SendMail, q_PowerManager))
        t_SetFlag = threading.Thread(target=o_Handlers.SetFlag,
                                     args=(q_SetFlag, q_Controller, q_PowerManagerFLAG))

        # Outbound shaping streams
        t_CreateAction = threading.Thread(target=o_Handlers.CreateAction,
                                          args=(q_Action, q_PrepareToSend, q_Internal))
        t_SendController = threading.Thread(target=o_Handlers.SendController,
                                            args=(q_PrepareToSend, q_TCPSend, q_Internal))

        # Database write processing
        t_DBWriteController = (threading.Thread(target=o_DB.WriteController,
                                                args=(q_DBWrite,)))
        # Service Streams
        t_CheckNewContent = threading.Thread(target=o_RenewCont.DynamicRenewCont,
                                             args=(q_PrepareToSend, q_Internal))
        t_UAValid = threading.Thread(target=o_Valid.UAValid,
                                     args=(q_UAValid, q_Internal))
        t_SendMailCont = threading.Thread(target=o_SendMailCont.SendMailController,
                                          args=(q_SendMail,))
        t_PowerManager = threading.Thread(target=o_Valid.PowerManager,
                                          args=(q_PowerManager, q_Internal, q_PowerManagerFLAG))

        LOG.CMSLogger('Threads are initialized')

        t_Init.start()
        t_Server.start()
        t_ClientUA.start()
        t_ReceiveDataFromUA.start()
        t_CreateAction.start()
        t_SendController.start()
        t_ValidDataScreen.start()
        t_ValidDataProc.start()
        t_CheckNewContent.start()

        t_Internal.start()
        t_UAValid.start()
        t_DBWriteController.start()
        t_SetFlag.start()
        t_SendMailCont.start()
        t_ClientContr.start()
        t_PowerManager.start()

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