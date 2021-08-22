# 1.1.1
import sys
from multiprocessing import Process, Queue


import threading
import queue

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import Valid
from App.Config import Config
from App import Resource, Comm, Handler, Control, Log

LOG = Log.Log_Manager()
LOG.CMSLogger('CALLED')

def main(Q_External):

    # Очереди
    Q_ValidScreenRAW = queue.Queue()
    Q_FromCore = queue.Queue()
    Q_ToSend = queue.Queue()
    Q_ProcStateRAW = queue.Queue()
    Q_ProcState = queue.Queue()
    Q_PrepareToSend = queue.Queue()
    Q_Action = queue.Queue()
    Q_Control = queue.Queue()

    # Экземпляры классов
    C_Valid = Valid.System()
    C_Handlers = Handler.Queue()
    C_Network = Comm.Socket()
    C_Handler = Handler.Queue()
    C_Validation = Valid.System()
    C_Control = Control.CMS()

    # Потоки
    T_Server = threading.Thread(target=C_Network.Server, args=(Config.localhost, Config.CMSUserAgentPort, Q_FromCore,))
    T_Client = threading.Thread(target=C_Network.Client, args=(Config.localhost, Config.CMSCoreInternalPort, Q_ToSend))

    T_ActionRun = threading.Thread(target=C_Handlers.UAAction, args=(Q_Action, Q_Control))
    T_GetScreen = threading.Thread(target=C_Control.GetScreenStatic, args=(Q_ValidScreenRAW,))
    T_CheckScreen = threading.Thread(target=C_Handlers.Valid, args=(Q_ValidScreenRAW, Q_PrepareToSend, True, 2, Resource.H[0], True,))
    T_GetProcState = threading.Thread(target=C_Control.GetProcessState, args=(Q_ProcStateRAW,))

    TQ_CheckProc = threading.Thread(target=C_Handler.CheckProcList, args=(Q_ProcStateRAW, Q_ProcState))
    TQ_ValidProc = threading.Thread(target=C_Handler.Valid, args=(Q_ProcState, Q_PrepareToSend, False, 1, Resource.H[0], True,))
    TQ_PrepareToSend = threading.Thread(target=C_Handlers.SendController, args=(Q_PrepareToSend, Q_ToSend,))
    TQ_FromCore = threading.Thread(target=C_Handlers.FromCore, args=(Q_FromCore, Q_Action))

    T_ThreadControl = threading.Thread(target=C_Control.Thread, args=(Q_Control, TQ_PrepareToSend, [T_Server, T_Client, T_ActionRun, T_GetScreen, T_CheckScreen,
                                                       T_GetProcState, TQ_CheckProc, TQ_ValidProc, TQ_PrepareToSend, TQ_FromCore, ],))

    # Запуск потоков
    T_Server.start()
    T_Client.start()
    T_ActionRun.start()
    T_GetScreen.start()
    T_CheckScreen.start()
    T_GetProcState.start()
    TQ_CheckProc.start()
    TQ_ValidProc.start()
    TQ_FromCore.start()
    TQ_PrepareToSend.start()

    T_ThreadControl.start()

    while True:
        data = Q_Control.get()
        Q_External.put(data)

if __name__ == '__main__':
    Q_External = Queue()
    proc = Process(target=main, args=(Q_External,))
    proc.start()
    while True:
        data = Q_External.get()
        if data == Resource.TerminateThread[0]:
            proc.kill()
            break
        else:
            pass