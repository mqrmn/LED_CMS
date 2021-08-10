#v.1.1.1

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
from App import LogManager, API, File, Comm, Resource, Action

import socket
import os
from App import LogManager
from inspect import currentframe, getframeinfo
logging = LogManager._Log_Manager_()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])


def TEST():
        C_Win = API.Win()
        C_FileMan = File.Manager()

        C_Action = Action.System()

        # Цикл
        # --------------------------------------------------------------------
        while True:

            if C_FileMan.CMSUpgrade(False) == True:
                logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Обнаружено обновление CMS')
                if C_Win.StopService('CMS')[0] == 0:
                    C_FileMan.CMSUpgrade(True)
                    logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Обновление установлено')
                    C_Action.Reboot()

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as Socket:
                try:
                    Socket.connect((Config.localhost, Config.CMSCoreInternalPort))
                    logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'OK', )
                except:
                    logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'FALL')


                    # C_Action.Reboot()
            time.sleep(30)


        # Граница цикла
        #----------------------------------------------------------------------

if __name__ == '__main__':
    TEST()