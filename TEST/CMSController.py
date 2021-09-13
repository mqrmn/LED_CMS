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
from App import Log, API, File, Comm, Act, Database, Control, Handler, Notify
from App import Resource as R



def TEST():
    LOG = Log.Log_Manager()

    LOG.CMSLogger('Controller initialized')

    # Creating class instances
    C_CMSUpgrade = File.CMSUpdate()
    C_Network = Comm.Socket()
    C_Control = Control.CMS()
    C_API = API.Service()
    O_SendMailCont = Notify.Mail()
    o_Handler = Handler.Queue()

    LOG.CMSLogger('Instances of classes created')

    # Queue creation
    Q_FromUpdater = queue.Queue()
    Q_FromCore = queue.Queue()
    Q_setFlag = queue.Queue()
    Q_SendMail = queue.Queue()
    q_internal = queue.Queue()
    Q_DBWrite = queue.Queue()

    LOG.CMSLogger('Queues created')

    # Thread initialization
    T_Updater = threading.Thread(target=C_CMSUpgrade.CMSUpdater,
                                 args=(Q_FromUpdater, q_internal,))
    T_Server = threading.Thread(target=C_Network.server,
                                args=(Config.localhost, Config.CMSControllertPort, Q_FromCore))

    T_FromCore = threading.Thread(target=o_Handler.FromCore,
                                  args=(Q_FromCore, q_internal))

    T_Internal = threading.Thread(target=o_Handler.Internal,
                                  args=(q_internal, None, Q_DBWrite, Q_setFlag, Q_SendMail))

    T_CMSServiceCont = threading.Thread(target=C_Control.cms_service,
                                        args=(Q_setFlag, Q_FromUpdater, q_internal))

    T_SendMailCont = threading.Thread(target=O_SendMailCont.SendMailController,
                                      args=(Q_SendMail,))

    LOG.CMSLogger('Threads are initialized')

    # Launching streams
    T_Updater.start()
    T_Server.start()
    T_FromCore.start()
    T_Internal.start()

    T_CMSServiceCont.start()
    T_SendMailCont.start()

    LOG.CMSLogger('Threads started')

    while True:
        time.sleep(10)



if __name__ == '__main__':
    TEST()