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
from App import Log, API, File, Comm, Act, Control, Handler, Database
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
        C_API = API.Service()
        C_CMSUpgrade = File.CMSUpdate()
        C_ActionSys = Act.System()
        C_ActionInit = Act.SysInit()
        C_Network = Comm.Socket()

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

        LOG.CMSLogger('Threads are initialized')

        # Launching streams
        T_Updater.start()
        T_Server.start()

        LOG.CMSLogger('Threads started')

        checkTime = datetime.datetime.now()
        table = Database.Tables()

        FLAG = C_ActionInit.CheckLastShutdown(Q_Manage)

        LOG = Log.Log_Manager()
        LOG.CMSLogger('CALLED')

        while True:
            if Q_Manage.empty() == False:
                FLAG = Q_Manage.get()[R.r[3]]

                LOG.CMSLogger('Reboot control flag: {}'.format(FLAG))

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as Socket:
                try:
                    Socket.connect((Config.localhost, Config.CMSCoreInternalPort))
                    checkTime = datetime.datetime.now()
                    LOG.CMSLogger('CMS Runned', )
                except:
                    if Q_Internal.empty() == False:
                        if Q_Internal.get() == True:
                            LOG.CMSLogger('CMS Stopped for upgrade', )
                            break
                        else:
                            pass
                    else:
                        LOG.CMSLogger('CMS Stopped', )
                        if FLAG > 0:
                            if FLAG > 1:
                                C_ActionSys.RebootInit()

                                LOG.CMSLogger('Reboot scheduled')
                                break
                            else:

                                lastReboot = table.SelfInitShutdown().select().order_by(
                                    table.SelfInitShutdown.id.desc()).get()
                                if (datetime.datetime.now() - lastReboot.datetime).seconds <= 300:
                                    C_ActionSys.RebootInit()

                                    LOG.CMSLogger('Reboot scheduled')
                                    break
                                else:
                                    LOG.CMSLogger('Restart access denied')
                        else:
                            LOG.CMSLogger('rRestart access denied')

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