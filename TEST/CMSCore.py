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
from App import Log, Comm, Resource, Handler, File, Act, Database, Control
from App import Resource as R

LOG = Log.Log_Manager()
LOG.CMSLogger('CALLED')

def TEST():
        # Core initialization
        Q_Internal = queue.Queue()
        C_Action = Act.SysInit()
        C_Action.InitCMS(Q_Internal)

        LOG.CMSLogger('Core initialized')

        C_Handlers = Handler.Queue()
        C_Network = Comm.Socket()
        C_RenewCont = File.RenewContent()
        C_Valid = Control.CMS()
        C_DB = Database.DBFoo()

        LOG.CMSLogger('Instances of classes created')

        Q_FromUA = queue.Queue()
        Q_Action = queue.Queue()
        Q_TCPSend = queue.Queue()
        Q_ValidProc = queue.Queue()
        Q_PrepareToSend = queue.Queue()
        Q_ValidScreen = queue.Queue()
        Q_SetFlag = queue.Queue()
        Q_UAValid = queue.Queue()
        Q_DBWrite = queue.Queue()
        Q_UAValidSF = queue.Queue()
        Q_Controller = queue.Queue()

        LOG.CMSLogger('Queues created')

        # Exchange threads
        T_Server = threading.Thread(target=C_Network.Server,
                                    args=(Config.localhost, Config.CMSCoreInternalPort, Q_FromUA))

        T_ClientUA = threading.Thread(target=C_Network.Client,
                                      args=(Config.localhost, Config.CMSUserAgentPort, Q_TCPSend))
        # T_ClientContr = threading.Thread(target=C_Network.Client,
        #                                  args=(Config.localhost, Config.CMSControllertPort, Q_TCPSend))

        # Inbound processing flows
        T_ReceiveDataFromUA = threading.Thread(target=C_Handlers.FromUA,
                                               args=(Q_FromUA, Q_ValidScreen, Q_ValidProc, Q_Internal))
        T_ValidDataScreen = threading.Thread(target=C_Handlers.Valid, args=(
                Q_ValidScreen, Q_Action, True, 1, R.H[0], True,))
        T_ValidDataProc = threading.Thread(target=C_Handlers.Valid,
                                           args=(Q_ValidProc, Q_Action, False, 1, R.H[0], True,))

        # Outbound shaping streams
        T_CreateAction = threading.Thread(target=C_Handlers.CreateAction, args=(Q_Action, Q_PrepareToSend, Q_SetFlag))
        T_SendController = threading.Thread(target=C_Handlers.SendController,
                                            args=(Q_PrepareToSend, Q_TCPSend, Q_SetFlag))

        # Internal processing flows
        T_Internal = threading.Thread(target=C_Handlers.Internal, args=(Q_Internal, Q_UAValid, Q_DBWrite, Q_SetFlag))
        T_SetFlag = threading.Thread(target=C_Handlers.SetFlag, args=(Q_SetFlag, Q_UAValidSF, Q_Controller))

        # Database write processing
        T_DBWriteController = (threading.Thread(target=C_DB.WriteController, args=(Q_DBWrite,)))

        # Service Streams
        T_CheckNewContent = threading.Thread(target=C_RenewCont.DynamicRenewCont, args=(Q_PrepareToSend,))
        T_UAValid = threading.Thread(target=C_Valid.UAValid, args=(Q_UAValid, Q_Internal, Q_UAValidSF))

        LOG.CMSLogger('Threads are initialized')

        T_Server.start()
        T_ClientUA.start()
        T_ReceiveDataFromUA.start()
        T_CreateAction.start()
        T_SendController.start()
        T_ValidDataScreen.start()
        T_ValidDataProc.start()
        T_CheckNewContent.start()

        T_Internal.start()
        T_UAValid.start()
        T_DBWriteController.start()
        T_SetFlag.start()

        LOG.CMSLogger('Threads started')


if __name__ == '__main__':
    TEST()
