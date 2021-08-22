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
from App import Log, API, File, Resource, Act, Control

import socket
from App import Log, Database, Comm, Handler



def TEST():
    # Создание экзепляров классов
    C_API = API.Service()
    C_FileMan = File.Manager()
    C_ActionSys = Act.System()
    C_ActionInit = Act.SysInit()
    C_Control = Control.CMS()
    C_Network = Comm.Socket()
    C_Handler = Handler.Queue()
    # Создание очередей
    Q_Internal = queue.Queue()
    Q_FromCore = queue.Queue()
    Q_Manage = queue.Queue()

    # Инициализация потоков
    T_Updater = threading.Thread(target=C_Control.CMSUpdater, args=(Q_Internal,))
    T_Server = threading.Thread(target=C_Network.Server,
                                args=(Config.localhost, Config.CMSControllertPort, Q_FromCore))
    # TQ_FromCore = threading.Thread(target=C_Handler.FromCore, args=(Q_FromCore, Q_Manage))

    # Запуск потоков
    T_Updater.start()
    T_Server.start()
    # TQ_FromCore.start()

    # Цикл
    # --------------------------------------------------------------------
    checkTime = datetime.datetime.now()
    table = Database.Tables()

    FLAG = C_ActionInit.CheckLastShutdown(Q_Manage)

    LOG = Log.Log_Manager()
    LOG.CMSLogger('CALLED')

    while True:
        if Q_Manage.empty() == False:
            FLAG = Q_Manage.get()[Resource.root[3]]

            LOG.CMSLogger('Флаг управления перезагрузкой: {}'.format(FLAG))

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

                            LOG.CMSLogger('reboot')
                            break
                        else:

                            lastReboot = table.SelfInitShutdown().select().order_by(
                                table.SelfInitShutdown.id.desc()).get()
                            if (datetime.datetime.now() - lastReboot.datetime).seconds <= 300:
                                C_ActionSys.RebootInit()

                                LOG.CMSLogger('reboot')
                                break
                            else:
                                LOG.CMSLogger('rebootAccessDenied')
                    else:
                        LOG.CMSLogger('rebootAccessDenied')

        time.sleep(10)


# Граница цикла
        #----------------------------------------------------------------------

if __name__ == '__main__':
    TEST()