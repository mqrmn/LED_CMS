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
from App import Log, Comm, Handler, File, Act, Database, Control, Notify
from App import Resource as Res

LOG = Log.LogManager()
LOG.cms_logger('CALLED')


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

        o_action = Act.SysInit()
        o_handlers = Handler.Queue()
        o_sockets = Comm.Socket()
        o_renew_cont = File.RenewContent()
        o_valid = Control.CMS()
        o_db = Database.DBFoo()
        o_send_mail_cont = Notify.Mail()

        LOG.cms_logger('Instances of classes created')

        q_internal = queue.Queue()
        q_from_ua = queue.Queue()
        q_action = queue.Queue()
        q_tcp_send = queue.Queue()
        q_valid_proc = queue.Queue()
        q_prepare_to_send = queue.Queue()
        q_valid_screen = queue.Queue()
        q_set_flag = queue.Queue()
        q_ua_valid = queue.Queue()
        q_db_write = queue.Queue()
        q_controller = queue.Queue()
        q_send_mail = queue.Queue()
        q_power_manager_flag = queue.Queue()
        q_power_manager = queue.Queue()

        LOG.cms_logger('Queues created')

        # 0 - out
        t_init = threading.Thread(target=o_action.init_cms,
                                  args=(q_internal,))
        # Exchange threads
        t_server = threading.Thread(target=o_sockets.server,
                                    args=(Config.localhost, Config.CMSCoreInternalPort, q_from_ua))
        t_client_ua = threading.Thread(target=o_sockets.client,
                                       args=(Config.localhost, Config.CMSUserAgentPort, q_tcp_send))

        # Inbound processing flows
        # 0 - in, 1, 2, 3 - out
        t_receive_data_from_ua = threading.Thread(target=o_handlers.from_ua,
                                                  args=(q_from_ua, q_valid_screen, q_valid_proc, q_internal))

        t_valid_data_screen = threading.Thread(target=o_handlers.valid,
                                               args=(q_valid_screen, q_action, True, 3, Res.H[0], True))
        t_valid_data_proc = threading.Thread(target=o_handlers.valid,
                                             args=(q_valid_proc, q_action, False, 3, Res.H[0], True))

        # Internal processing flows
        t_internal = threading.Thread(target=o_handlers.internal,
                                      args=(q_internal, q_ua_valid, q_db_write,
                                            q_set_flag, q_send_mail, q_power_manager))
        t_set_flag = threading.Thread(target=o_handlers.set_flag,
                                      args=(q_set_flag, q_controller, q_power_manager_flag))

        # Outbound shaping streams
        # 0 - in, 1, 2 - out
        t_create_action = threading.Thread(target=o_handlers.create_action,
                                           args=(q_action, q_prepare_to_send, q_internal))

        t_send_controller = threading.Thread(target=o_handlers.send_controller,
                                             args=(q_prepare_to_send, q_tcp_send,))

        # Database write processing
        t_db_write_controller = (threading.Thread(target=o_db.write_controller,
                                                  args=(q_db_write,)))
        # Service Streams
        # 0, 1 - out
        t_check_new_content = threading.Thread(target=o_renew_cont.dynamic_renew_cont,
                                               args=(q_prepare_to_send, q_internal))
        # 0 - in, 1 - out
        t_ua_valid = threading.Thread(target=o_valid.ua_valid,
                                      args=(q_ua_valid, q_internal))
        t_send_mail_cont = threading.Thread(target=o_send_mail_cont.send_mail_controller,
                                            args=(q_send_mail,))
        # 0, 2 - in, 1 - out
        t_power_manager = threading.Thread(target=o_valid.power_manager,
                                           args=(q_power_manager, q_internal, q_power_manager_flag))

        LOG.cms_logger('Threads are initialized')

        t_init.start()
        t_server.start()
        t_client_ua.start()
        t_receive_data_from_ua.start()
        t_create_action.start()
        t_send_controller.start()
        t_valid_data_screen.start()
        t_valid_data_proc.start()
        t_check_new_content.start()

        t_internal.start()
        t_ua_valid.start()
        t_db_write_controller.start()
        t_set_flag.start()
        t_send_mail_cont.start()
        t_power_manager.start()

        LOG.cms_logger('Threads started')

        while True:
            time.sleep(10)

            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            if rc == win32event.WAIT_OBJECT_0:
                LOG.cms_logger('Command to stop service received')
                c_comm = Comm.Socket()
                c_comm.send(Config.localhost, Config.CMSUserAgentPort, Res.TerminateThread[0])
                LOG.cms_logger('UA stop command sent')
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
