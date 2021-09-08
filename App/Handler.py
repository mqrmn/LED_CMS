# 1.1.1

import sys
import time
import datetime
from inspect import currentframe, getframeinfo

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import File, Act, Database, Log, Notify
from App import Resource as R
from App.Config import Config as C

LOG = Log.Log_Manager()

class Init:
    def __init__(self):
        global o_CrMsg
        global o_Act
        global o_DBMsg
        global o_crMailMsg


        o_DBMsg = Database.Prepare()
        o_CrMsg = R.CreateMessage()
        o_Act = Act.System()
        o_crMailMsg = Notify.Mail()

# Queue handlers
class Queue(Init):
    def SendController(self, Q_in, Q_out, q_Internal=None,):

        NullDatetime = datetime.datetime.strptime('2020-02-02', "%Y-%m-%d")

        termNovaTime = NullDatetime
        termMarsTime = NullDatetime
        resNovaTime = NullDatetime
        runNovaTime = NullDatetime


        while True:
            data = Q_in.get()

            # Launching NovaStudio
            if data == R.RunNova[1]:
                if ((datetime.datetime.now() - runNovaTime).seconds >= C.runNovaTimeout):
                    self.ToSend(data, Q_out)
                    runNovaTime = datetime.datetime.now()
                else:
                    pass
                data = None
            # Stop NovaStudio
            if data == R.TerminateNova:
                if ((datetime.datetime.now() - termNovaTime).seconds >= C.terminateNovaTimeout):
                    self.ToSend(data, Q_out)
                    termNovaTime = datetime.datetime.now()
                else:
                    pass
                    data = None
            # Stopping MarsServerProvider
            if data == R.TerminateMars[1]:
                if ((datetime.datetime.now() - termMarsTime).seconds >= C.terminateMarsTimeout):
                    self.ToSend(data, Q_out)
                    termMarsTime = datetime.datetime.now()
                else:
                    pass
                data = None
            # Restarting NovaStudio
            if data == R.RestartNova[1]:
                if ((datetime.datetime.now() - resNovaTime).seconds >= C.restartNovaTimeout):
                    self.ToSend(data, Q_out)
                    resNovaTime = datetime.datetime.now()
                else:
                    pass
                data = None

            if data != None:
                self.ToSend(data, Q_out)

    # Handler for the queue of data coming from CMSUserAgent
    def FromUA(self, Q_in, Q_screenValidation, Q_procValidation, Q_Internal):
        while True:
            data = Q_in.get()
            lastReceive = datetime.datetime.now()
            if data[R.r[0]] == R.M[0]:
                if data[R.r[1]] == R.H[0]:
                    if data[R.r[2]] == R.K[0]:
                        Q_screenValidation.put({R.r[2]: data[R.r[2]], R.r[3]: data[R.r[3]], })
                    if data[R.r[2]] == R.K[1]:
                        Q_procValidation.put({R.r[2]: data[R.r[2]], R.r[3]: data[R.r[3]], })

            Q_Internal.put({R.r[1]: R.H[2],
                            R.r[2]: R.K[7],
                            R.r[3]: lastReceive, })


    # Prepares commands to be sent to the UA
    def CreateAction(self, Q_in, Q_out, q_Internal ):
        restartNovaCount = 0
        restoreNovaCount = 0
        lastNovaRestart = None
        DictNova = {}
        DictMars = {}
        command = None


        while True:

            data = Q_in.get()
            if (data[R.r[2]] == R.K[0]) \
                    or (data[R.r[2]] == R.K[1]
                        and data[R.r[3]][0] == R.ProcList[0]):
                DictNova[data[R.r[2]]] = data[R.r[3]]

                # Run Nova
                if DictNova == R.RunNova[0]:
                    command = R.RunNova[1]
                    DictNova = {}
                # Restart Nova
                if DictNova == R.RestartNova[0]:
                    command = R.RestartNova[1]
                    DictNova = {}
                    restartNovaCount += 1
                    lastNovaRestart = datetime.datetime.now()
                if command:
                    Q_out.put(command)
                    command = None
                    DictNova = {}

            if data[R.r[2]] == R.K[1] \
                    and data[R.r[3]][0] == R.ProcList[1]:
                DictMars[data[R.r[2]]] = data[R.r[3]]
                # TerminateMars
                if DictMars == R.TerminateMars[0]:
                    command = R.TerminateMars[1]
                    DictMars = {}
                if command:
                    Q_out.put(command)
                    command = None
                    DictMars = {}
            # RestoreNova
            if restartNovaCount >= C.restartNovaMaxCount \
                    and ((datetime.datetime.now() - lastNovaRestart).seconds <= C.restartNovaTimeout):
                Q_out.put(R.RestoreNovaBin[0])
                restoreNovaCount += 1
                restartNovaCount = 0
                if restoreNovaCount >= C.restoreNovaMaxCount:
                    q_Internal.put(o_CrMsg.RebootSystem())
                    q_Internal.put(o_crMailMsg.SendMail('The system attempt to reboot'))


    # Processor of data coming to UA
    def FromCore(self, Q_in, Q_out, ):
        while True:
            data = Q_in.get()
            if data[R.r[0]] == R.M[0]:      # Method == put
                if data[R.r[1]] == R.H[1]:  # Head == Action
                    Q_out.put(data)
                if data[R.r[1]] == R.H[4]:  # Head == Flag
                    Q_out.put(data[R.r[3]])

    def FromCoreToCont(self, Q_in, Q_out, ):
        data = Q_in.get()
        if data[R.r[0]] == R.M[0]:  # Method == put
            if data[R.r[1]] == R.H[4]:  # Head == Flag
                Q_out.put(data)


    # Checks the keys in the data coming to the UA, in accordance with them, launches actions
    def UAAction(self, Q_in, Q_out,):
        C_Exec = Act.Process()
        C_File = File.NovaBin()
        while True:
            data = Q_in.get()
            if data[R.r[2]] == R.K[2]:      # Key == RunProc
                C_Exec.Start(data[R.r[3]])
            if data[R.r[2]] == R.K[3]:      # Key == TerminateProc
                C_Exec.Terminate(data[R.r[3]])
            if data[R.r[2]] == R.K[4]:      # Key == RestartProc
                C_Exec.Restart(data[R.r[3]])
            if data[R.r[2]] == R.K[5]:      # Key == Process
                pass
            if data[R.r[2]] == R.K[6]:      # Key == TerminateThread
                Q_out.put(data)
            if data[R.r[2]] == R.K[11]:     # Key == RestoreNovaBin
                C_File.RestoreHandle()


    # Checks the flow of incoming data for a given match
    def Valid(self, Q_in, Q_out, checkValue, maxCount, head, sendAllCircles, ):
        checkCount, catchCount = 0, 0
        Dict = {}

        while True:
            data = Q_in.get()
            if type(data) == dict:
                if data[R.r[3]][0] not in Dict:
                    Dict[data[R.r[3]][0]] = 0
                else:
                    pass
                checkCount += 1
                if data[R.r[3]][1] == checkValue:
                    Dict[data[R.r[3]][0]] += 1
                else:
                    pass
                if Dict.__len__() > 1:
                    maxCountH = maxCount * Dict.__len__()
                else:
                    maxCountH = maxCount
                if checkCount >= maxCountH:
                    for i in Dict:
                        if Dict[i] == maxCount:
                            Q_out.put({R.r[1]: head, R.r[2]: data[R.r[2]], R.r[3]: [i, checkValue]})
                        else:
                            if sendAllCircles == True:
                                Q_out.put({R.r[1]: head, R.r[2]: data[R.r[2]], R.r[3]: [i, not checkValue]})
                            else:
                                pass
                    Dict = {}
                    checkCount, catchCount = 0, 0
                else:
                    pass

    # Checking the list of processes for compliance with the activity status
    def CheckProcList(self, Q_in, Q_out):
        while True:
            if Q_in.empty() == False:
                data = Q_in.get()
                if data[1] == R.ProcDict[data[0]]:
                    state = True
                else:
                    state = False
                Q_out.put({R.r[2]: R.K[1], R.r[3]: [data[0], state]})
            else:
                time.sleep(1)

    # Send queue processing
    def ToSend(self, data, Q_out):
        data[R.r[0]] = R.M[0]
        Q_out.put(data)

    # Internal queue processing
    def Internal(self, q_internal, Q_UAValid, Q_DBWrite, Q_SetFlag, Q_SendMail, q_PowerManager=None):
        while True:
            data = q_internal.get()

            # Agent check
            if data[R.r[1]] == R.H[2]:
                if data[R.r[2]] == R.K[7]:
                    Q_UAValid.put(data[R.r[3]])
            # Write to the database
            if data[R.r[1]] == R.H[3]:
                if data[R.r[2]] == R.K[8]:
                    Q_DBWrite.put(data[R.r[3]])
            # Set flags
            if data[R.r[1]] == R.H[4]:
                Q_SetFlag.put({R.r[2]: data[R.r[2]],
                               R.r[3]: data[R.r[3]], }, )
            # Send Mail
            if data[R.r[1]] == R.H[5]:
                Q_SendMail.put(data[R.r[3]])
            if data[R.r[2]] == R.K[13]:
                q_PowerManager.put(data)

    def SetFlag(self, Q_SetFlag, Q_Cont_TCPSend, q_SendContrSetFLAG):
        while True:
            data = Q_SetFlag.get()
            if data[R.r[2]] == R.K[9]:
                q_SendContrSetFLAG.put(data[R.r[3]])
            if data[R.r[2]] == R.K[10]:
                Q_Cont_TCPSend.put({R.r[0]: R.M[0], R.r[1]: R.H[4],
                                    R.r[2]: R.K[10], R.r[3]: data[R.r[3]]})


