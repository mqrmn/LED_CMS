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
from App import LogManager
from inspect import currentframe, getframeinfo
logging = LogManager._Log_Manager_()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])


def TEST():
        # Создание экзепляров классов
        C_Win = API.Win()
        C_FileMan = File.Manager()
        C_Action = Action.System()
        C_Control = Controller.CMS()

        # Создание очередей
        Q_Internal = queue.Queue()

        # Инициализация потоков
        T_Updater = threading.Thread(target=C_Control.CMSUpdater, args=(Q_Internal, ))

        # Запуск потоков
        T_Updater.start()


        # Цикл
        # --------------------------------------------------------------------
        checkTime = datetime.datetime.now()
        while True:
            print((checkTime - datetime.datetime.now()).seconds)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as Socket:
                try:
                    Socket.connect((Config.localhost, Config.CMSCoreInternalPort))
                    checkTime = datetime.datetime.now()
                    logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'СЛУЖБА ЗАПУЩЕНА', )
                except:

                    if Q_Internal.empty() == False:
                        if Q_Internal.get() == True:
                            logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'СЛУЖБА ОСТАНОВЛЕНА ВСВЯЗИ С ОБНОВЛЕНИЕМ', )
                            break

                        else:
                            pass
                    else:
                        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'СЛУЖБА ОСТАНОВЛЕНА', )
                        if ((checkTime - datetime.datetime.now()).seconds >= 300):
                            logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'REBOOT')
                            C_Action.Reboot()
                            break


            time.sleep(30)


        # Граница цикла
        #----------------------------------------------------------------------

if __name__ == '__main__':
    TEST()