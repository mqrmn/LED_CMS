# v.1.1.1

from App import Validation
import threading
import queue

from App.Config import Config
from App import Resource, Comm, Handler

def main():

    # Очереди
    Q_ValidScreenRAW = queue.Queue()                    # Очередь результатов проверки экрана
    Q_FromCore = queue.Queue()
    Q_ToSend = queue.Queue()
    Q_ProcStateRAW = queue.Queue()
    Q_ProcState = queue.Queue()
    Q_PrepareToSend = queue.Queue()
    Q_Action = queue.Queue()

    # Экземпляры классов
    C_Valid = Validation._System_()                   # Экземпляр класса валидации
    C_Handlers = Handler.Queue()
    C_Network = Comm.Socket()
    C_Handler = Handler.Queue()
    C_Validation = Validation._System_()

    # Потоки
    T_Server = threading.Thread(target=C_Network.Server, args=(Config.localhost, Config.CMSUserAgentPort, Q_FromCore,))
    T_Client = threading.Thread(target=C_Network.Client, args=(Config.localhost, Config.CMSCoreInternalPort, Q_ToSend))
    T_ActionRun = threading.Thread(target=C_Handlers.UAAction, args=(Q_Action, Q_PrepareToSend))
    T_GetScreen = threading.Thread(target=C_Valid.GetScreenStatic, args=(Q_ValidScreenRAW,))
    T_CheckScreen = threading.Thread(target=C_Handlers.Valid, args=(Q_ValidScreenRAW, Q_PrepareToSend, True, 4, Resource.ComDict['head'][0], True, ))
    T_GetProcState = threading.Thread(target=C_Validation.GetProcessState, args=(Q_ProcStateRAW,))
    TQ_CheckProc = threading.Thread(target=C_Handler.CheckProcList, args=(Q_ProcStateRAW, Q_ProcState))
    TQ_ValidProc = threading.Thread(target=C_Handler.Valid, args=(Q_ProcState, Q_PrepareToSend, False, 2, Resource.ComDict['head'][0], True, ))
    TQ_PrepareToSend = threading.Thread(target=C_Handlers.PrepareToSend, args=(Q_PrepareToSend, Q_ToSend, ))
    TQ_FromCore = threading.Thread(target=C_Handlers.FromCore, args=(Q_FromCore, Q_Action))

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

# if __name__ == '__main__':
#     main()





