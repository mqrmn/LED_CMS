# 1.1.1

import sys
import win32serviceutil
import win32service
import win32event
import servicemanager
import time
import datetime
import threading
import queue
import socket

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config
from App import Log, API, File, Comm, Act, Database, Control
from App import Resource as R





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

        LOG = Log.Log_Manager()

        LOG.CMSLogger('Controller initialized')

        # Creating class instances
        C_CMSUpgrade = File.CMSUpdate()
        C_Network = Comm.Socket()
        C_Control = Control.CMS()
        C_API = API.Service()

        LOG.CMSLogger('Instances of classes created')

        # Queue creation
        Q_Internal = queue.Queue()
        Q_FromCore = queue.Queue()
        Q_Manage = queue.Queue()

        LOG.CMSLogger('Queues created')

        # Thread initialization
        T_Updater = threading.Thread(target=C_CMSUpgrade.CMSUpdater, args=(Q_Internal,))
        T_Server = threading.Thread(target=C_Network.Server,
                                    args=(Config.localhost, Config.CMSControllertPort, Q_FromCore))
        T_CMSServiceCont = threading.Thread(target=C_Control.CMSService, args=(Q_Manage, Q_Internal,))

        LOG.CMSLogger('Threads are initialized')

        # Launching streams
        T_Updater.start()
        T_Server.start()
        T_CMSServiceCont.start()

        LOG.CMSLogger('Threads started')

        while True:
            time.sleep(10)

            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            if rc == win32event.WAIT_OBJECT_0:
                C_API.StopService('CMS')
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