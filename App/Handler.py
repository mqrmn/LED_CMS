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
    def SendController(self, q_prepare_to_send, q_tcp_send, q_internal=None, ):

        NullDatetime = datetime.datetime.strptime('2020-02-02', "%Y-%m-%d")

        termNovaTime = NullDatetime
        termMarsTime = NullDatetime
        resNovaTime = NullDatetime
        runNovaTime = NullDatetime


        while True:
            data = q_prepare_to_send.get()

            # Launching NovaStudio
            if data == R.RunNova[1]:
                if ((datetime.datetime.now() - runNovaTime).seconds >= C.runNovaTimeout):
                    self.ToSend(data, q_tcp_send)
                    runNovaTime = datetime.datetime.now()
                else:
                    pass
                data = None
            # Stop NovaStudio
            if data == R.TerminateNova:
                if ((datetime.datetime.now() - termNovaTime).seconds >= C.terminateNovaTimeout):
                    self.ToSend(data, q_tcp_send)
                    termNovaTime = datetime.datetime.now()
                else:
                    pass
                data = None
            # Stopping MarsServerProvider
            if data == R.TerminateMars[1]:
                if ((datetime.datetime.now() - termMarsTime).seconds >= C.terminateMarsTimeout):
                    self.ToSend(data, q_tcp_send)
                    termMarsTime = datetime.datetime.now()
                else:
                    pass
                data = None
            # Restarting NovaStudio
            if data == R.RestartNova[1]:
                if ((datetime.datetime.now() - resNovaTime).seconds >= C.restartNovaTimeout):
                    self.ToSend(data, q_tcp_send)
                    resNovaTime = datetime.datetime.now()
                else:
                    pass
                data = None

            if data != None:
                self.ToSend(data, q_tcp_send)

    # Handler for the queue of data coming from CMSUserAgent
    def FromUA(self, q_from_ua, q_valid_screen, q_valid_proc, q_internal):
        while True:
            data = q_from_ua.get()
            lastReceive = datetime.datetime.now()
            if data[R.r[0]] == R.M[0]:
                if data[R.r[1]] == R.H[0]:
                    if data[R.r[2]] == R.K[0]:
                        q_valid_screen.put({R.r[2]: data[R.r[2]], R.r[3]: data[R.r[3]], })
                    if data[R.r[2]] == R.K[1]:
                        q_valid_proc.put({R.r[2]: data[R.r[2]], R.r[3]: data[R.r[3]], })

            q_internal.put({R.r[1]: R.H[2],
                            R.r[2]: R.K[7],
                            R.r[3]: lastReceive, })


    # Prepares commands to be sent to the UA
    def CreateAction(self, q_action, q_prepare_to_send, q_internal):
        restartNovaCount = 0
        restoreNovaCount = 0
        lastNovaRestart = None
        DictNova = {}
        DictMars = {}
        command = None


        while True:

            data = q_action.get()
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
                    q_prepare_to_send.put(command)
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
                    q_prepare_to_send.put(command)
                    command = None
                    DictMars = {}
            # RestoreNova
            if restartNovaCount >= C.restartNovaMaxCount \
                    and ((datetime.datetime.now() - lastNovaRestart).seconds <= C.restartNovaTimeout):
                q_prepare_to_send.put(R.RestoreNovaBin[0])
                restoreNovaCount += 1
                restartNovaCount = 0
                if restoreNovaCount >= C.restoreNovaMaxCount:
                    a = o_CrMsg.RebootSystem()
                    b = o_CrMsg.SendMail('The system attempt to reboot')
                    q_internal.put(a)
                    q_internal.put(b)


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
                C_Exec.start(data[R.r[3]])
            if data[R.r[2]] == R.K[3]:      # Key == TerminateProc
                C_Exec.terminate(data[R.r[3]])
            if data[R.r[2]] == R.K[4]:      # Key == RestartProc
                C_Exec.restart(data[R.r[3]])
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
    def Internal(self, q_internal, q_ua_valid, q_db_write, q_set_flag, q_send_mail, q_power_manager=None):
        while True:
            data = q_internal.get()
            # Agent check
            if data[R.r[1]] == R.H[2]:
                if data[R.r[2]] == R.K[7]:
                    q_ua_valid.put(data[R.r[3]])
            # Write to the database
            if data[R.r[1]] == R.H[3]:
                if data[R.r[2]] == R.K[8]:
                    q_db_write.put(data[R.r[3]])
            # Set flags
            if data[R.r[1]] == R.H[4]:
                q_set_flag.put({R.r[2]: data[R.r[2]],
                                R.r[3]: data[R.r[3]], }, )
            # Send Mail
            if data[R.r[1]] == R.H[5]:
                q_send_mail.put(data[R.r[3]])
            if data[R.r[2]] == R.K[13]:
                q_power_manager.put(data)

    def SetFlag(self, q_set_flag, q_controller, q_power_manager_flag):
        while True:
            data = q_set_flag.get()
            if data[R.r[2]] == R.K[9]:
                q_power_manager_flag.put(data[R.r[3]])
            if data[R.r[2]] == R.K[10]:
                q_controller.put({R.r[0]: R.M[0], R.r[1]: R.H[4],
                                  R.r[2]: R.K[10], R.r[3]: data[R.r[3]]})


