# 1.1.1

import sys
import threading
import queue
from multiprocessing import Process, Queue

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import  Comm, Handler, Control, Log
from App.Config import Config as C
from App import Resource as R

LOG = Log.Log_Manager()

def main(Q_External):

    q_screenRawData = queue.Queue()
    q_dataFromCore = queue.Queue()
    q_dataToTCPSend = queue.Queue()
    q_procStateRawData = queue.Queue()
    q_ProcStateData = queue.Queue()
    q_forPrepareToSend = queue.Queue()
    q_actionData = queue.Queue()
    q_control = queue.Queue()

    LOG.CMSLogger('Queues created')

    o_Handlers = Handler.Queue()
    o_Network = Comm.Socket()
    o_Handler = Handler.Queue()
    o_Control = Control.CMS()

    LOG.CMSLogger('Instances of classes created')

    t_TCPServer = threading.Thread(target=o_Network.Server,
                                   args=(C.address, C.CMSUserAgentPort, q_dataFromCore,))
    t_TCPClient = threading.Thread(target=o_Network.Client,
                                   args=(C.address, C.CMSCoreInternalPort, q_dataToTCPSend))

    t_ActionRun = threading.Thread(target=o_Handlers.UAAction,
                                   args=(q_actionData, q_control))
    t_GetScreen = threading.Thread(target=o_Control.GetScreenStatic,
                                   args=(q_screenRawData,))
    t_CheckScreen = threading.Thread(target=o_Handlers.Valid,
                                     args=(q_screenRawData, q_forPrepareToSend, True, C.checkScrCountUA, R.H[0], True,))
    t_GetProcState = threading.Thread(target=o_Control.GetProcessState,
                                      args=(q_procStateRawData,))

    t_CheckProc = threading.Thread(target=o_Handler.CheckProcList,
                                   args=(q_procStateRawData, q_ProcStateData))
    t_ValidProc = threading.Thread(target=o_Handler.Valid,
                                   args=(q_ProcStateData, q_forPrepareToSend, False, C.checkProcCountUA, R.H[0], True,))
    t_PrepareToSend = threading.Thread(target=o_Handlers.SendController,
                                       args=(q_forPrepareToSend, q_dataToTCPSend, ))
    t_FromCore = threading.Thread(target=o_Handlers.FromCore,
                                  args=(q_dataFromCore, q_actionData))

    t_ThreadControl = threading.Thread(target=o_Control.Thread,
                                       args=(q_control, t_PrepareToSend, [t_TCPServer,
                                            t_TCPClient, t_ActionRun, t_GetScreen,
                                            t_CheckScreen, t_GetProcState, t_CheckProc,
                                            t_ValidProc, t_PrepareToSend, t_FromCore, ],))


    LOG.CMSLogger('Threads are initialized')

    t_TCPServer.start()
    t_TCPClient.start()
    t_ActionRun.start()
    t_GetScreen.start()
    t_CheckScreen.start()
    t_GetProcState.start()
    t_CheckProc.start()
    t_ValidProc.start()
    t_FromCore.start()
    t_PrepareToSend.start()
    t_ThreadControl.start()

    LOG.CMSLogger('Threads started')

    while True:
        data = q_control.get()
        Q_External.put(data)

if __name__ == '__main__':

    q_External = Queue()
    proc = Process(target=main, args=(q_External,))
    proc.start()

    LOG.CMSLogger('Process started')
    while True:
        data = q_External.get()
        if data == R.TerminateThread[0]:
            proc.kill()
            LOG.CMSLogger('Process terminated')
            break
        else:
            pass