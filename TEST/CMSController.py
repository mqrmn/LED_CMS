#v.1.1.1
import datetime
import sys
sys.path.append("C:\\MOBILE\\Local\\CMS")

import win32serviceutil
import win32service
import win32event
import servicemanager
import time
import os
import threading
import queue

from App.Config import Config
from App import LogManager, API, File, Comm, Resource, Action, Controller

import socket
import os
from App import LogManager, Database, Comm, Handler
from inspect import currentframe, getframeinfo
logging = LogManager._Log_Manager_()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])


def TEST():
    # Создание экзепляров классов
    C_Win = API.Win()
    C_FileMan = File.Manager()
    C_Action = Action.System()
    C_Control = Controller.CMS()
    C_Network = Comm.Socket()
    C_Handler = Handler.Queue()
    # Создание очередей
    Q_Internal = queue.Queue()
    Q_FromCore = queue.Queue()
    Q_Manage = queue.Queue()

    # Инициализация потоков
    T_Updater = threading.Thread(target=C_Control.CMSUpdater, args=(Q_Internal,))
    T_Server = threading.Thread(target=C_Network.Server, args=(Config.localhost, Config.CMSControllertPort, Q_FromCore))
    TQ_FromCore = threading.Thread(target=C_Handler.FromCore, args=(Q_FromCore, Q_Manage))

    # Запуск потоков
    T_Updater.start()

    # Цикл
    # --------------------------------------------------------------------
    checkTime = datetime.datetime.now()
    while True:
        if Q_Manage.empty() == False:
            FLAG = Q_Manage.get()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as Socket:
            try:
                Socket.connect((Config.localhost, Config.CMSCoreInternalPort))
                checkTime = datetime.datetime.now()
                logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'CMS Runned', )
            except:

                if Q_Internal.empty() == False:
                    if Q_Internal.get() == True:
                        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2],
                                          'CMS Stopped for upgrade', )
                        break

                    else:
                        pass
                else:
                    logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'CMS Stopped', )
                    if ((checkTime - datetime.datetime.now()).seconds >= 300):
                        table = Database.Tables()
                        table.SelfInitShutdown.create(trigger='CMSController',
                                                      key='reboot',
                                                      datetime=datetime.datetime.now(), )
                        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'REBOOT')
                        C_Action.Reboot()
                        break

        time.sleep(30)


        # Граница цикла
        #----------------------------------------------------------------------

if __name__ == '__main__':
    TEST()