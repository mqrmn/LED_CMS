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



def TEST():
    LOG = Log.Log_Manager()

    LOG.CMSLogger('Controller initialized')

    # Creating class instances
    C_CMSUpgrade = File.CMSUpdate()
    C_Network = Comm.Socket()
    C_Control = Control.CMS()

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



if __name__ == '__main__':
    TEST()