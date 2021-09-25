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

from App.Config import Config as Con
from App import Log, API, File, Comm, Control, Notify, Handler


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

        log = Log.LogManager()

        log.cms_logger('Controller initialized')

        # Creating class instances
        o_cms_upgrade = File.CMSUpdate()
        o_network = Comm.Socket()
        o_control = Control.CMS()
        o_api = API.Service()
        o_send_mail_cont = Notify.Mail()
        o_handlers = Handler.Queue()

        log.cms_logger('Instances of classes created')

        # Queue creation
        q_from_updater = queue.Queue()
        q_from_core = queue.Queue()
        q_set_flag = queue.Queue()
        q_send_mail = queue.Queue()
        q_internal = queue.Queue()
        q_db_write = queue.Queue()

        log.cms_logger('Queues created')

        # Thread initialization
        t_updater = threading.Thread(target=o_cms_upgrade.cms_updater,
                                     args=(q_from_updater, q_internal,))
        t_server = threading.Thread(target=o_network.server,
                                    args=(Con.localhost, Con.CMSControllertPort, q_from_core))

        t_from_core = threading.Thread(target=o_handlers.from_core,
                                       args=(q_from_core, q_internal))

        t_internal = threading.Thread(target=o_handlers.internal,
                                      args=(q_internal, None, q_db_write, q_set_flag, q_send_mail))

        t_cms_service_cont = threading.Thread(target=o_control.cms_service,
                                              args=(q_set_flag, q_from_updater))

        t_send_mail_cont = threading.Thread(target=o_send_mail_cont.send_mail_controller,
                                            args=(q_send_mail,))

        log.cms_logger('Threads are initialized')

        # Launching streams
        t_updater.start()
        t_server.start()
        t_from_core.start()
        t_internal.start()

        t_cms_service_cont.start()
        t_send_mail_cont.start()

        log.cms_logger('Threads started')

        while True:
            time.sleep(10)

            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            if rc == win32event.WAIT_OBJECT_0:
                o_api.stop_service('CMS')
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
