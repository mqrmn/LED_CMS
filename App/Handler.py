# 1.1.1

import sys
import time
import datetime

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import Act,  Log
from App import Resource as R


# Queue handlers
class Queue:
    def SendController(self, Q_in, Q_out, Q_SetFlag = None, ):
        termNovaCount = 0
        termMarsCount = 0
        resNovaCount = 0
        runNovaCount = 0
        termNovaTime = datetime.datetime.now()
        termMarsTime = datetime.datetime.now()
        resNovaTime = datetime.datetime.now()
        runNovaTime = datetime.datetime.now()

        while True:
            data = Q_in.get()
            if Q_SetFlag != None:
                if Q_SetFlag.empty() == False:
                    flag = Q_SetFlag.get()
                else:
                    pass
            else:
                pass
            # Launching NovaStudio
            if data == R.RunNova[1]:
                if ((datetime.datetime.now() - runNovaTime).seconds >= 30) or runNovaCount == 0:
                    self.ToSend(data, Q_out)
                    runNovaTime = datetime.datetime.now()
                    runNovaCount += 1
                else:
                    pass
                data = None
            # Stop NovaStudio
            if data == R.TerminateNova:
                if ((datetime.datetime.now() - termNovaTime).seconds >= 30) or termNovaCount == 0:
                    self.ToSend(data, Q_out)
                    termNovaTime = datetime.datetime.now()
                    termNovaCount += 1
                else:
                    pass
                    data = None
            # Stopping MarsServerProvider
            if data == R.TerminateMars[1]:
                if ((datetime.datetime.now() - termMarsTime).seconds >= 30) or termMarsCount == 0:
                    self.ToSend(data, Q_out)
                    termMarsTime = datetime.datetime.now()
                    termMarsCount += 1
                else:
                    pass
                data = None
            # Restarting NovaStudio
            if data == R.RestartNova[1]:
                if ((datetime.datetime.now() - resNovaTime).seconds >= 30) or resNovaCount == 0:
                    self.ToSend(data, Q_out)
                    resNovaTime = datetime.datetime.now()
                    resNovaCount += 1
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
    def CreateAction(self, Q_in, Q_out, Q_SetFlag):
        DictNova = {}
        DictMars = {}
        command = None
        while True:
            data = Q_in.get()
            if (data[R.r[2]] == R.K[0]) or (data[R.r[2]] == R.K[1] and data[R.r[3]][0] == R.ProcList[0]):
                DictNova[data[R.r[2]]] = data[R.r[3]]

                if DictNova == R.RunNova[0]:
                    command = R.RunNova[1]
                    DictNova = {}
                if DictNova == R.RestartNova[0]:
                    command = R.RestartNova[1]
                    DictNova = {}
                if command:
                    Q_out.put(command)
                    command = None
                    DictNova = {}

            if data[R.r[2]] == R.K[1] and data[R.r[3]][0] == R.ProcList[1]:
                DictMars[data[R.r[2]]] = data[R.r[3]]
                if DictMars == R.TerminateMars[0]:
                    command = R.TerminateMars[1]
                    DictMars = {}
                if command:
                    Q_out.put(command)
                    command = None
                    DictMars = {}

    # Processor of data coming to UA
    def FromCore(self, Q_in, Q_out, ):
        while True:
            data = Q_in.get()
            if data[R.r[0]] == R.M[0]:
                if data[R.r[1]] == R.H[1]:
                    Q_out.put(data)
                if data[R.r[1]] == R.H[4]:
                    Q_out.put(data[R.r[3]])

    # Checks the keys in the data coming to the UA, in accordance with them, launches actions
    def UAAction(self, Q_in, Q_out,):
        Exec = Act.Process()
        while True:
            data = Q_in.get()
            if data[R.r[2]] == R.K[2]:
                Exec.Start(data[R.r[3]])
            if data[R.r[2]] == R.K[3]:
                Exec.Terminate(data[R.r[3]])
            if data[R.r[2]] == R.K[4]:
                Exec.Restart(data[R.r[3]])
            if data[R.r[2]] == R.K[5]:
                pass
            if data[R.r[2]] == R.K[6]:
                Q_out.put(data)

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
    def Internal(self, Q_in, Q_UAValid, Q_DBWrite, Q_SetFlag):
        while True:
            data = Q_in.get()
            # Проверка агента
            if data[R.r[1]] == R.H[2]:
                if data[R.r[2]] == R.K[7]:
                    Q_UAValid.put(data[R.r[3]])
            # Запись в БД
            if data[R.r[1]] == R.H[3]:
                if data[R.r[2]] == R.K[8]:
                    Q_DBWrite.put(data[R.r[3]])
            # Установка флагов
            if data[R.r[1]] == R.H[4]:
                Q_SetFlag.put({R.r[2]: data[R.r[2]],
                               R.r[3]: data[R.r[3]], }, )

    def SetFlag(self, Q_SetFlag, Q_UAValidSF, Q_Cont_TCPSend):
        while True:
            data = Q_SetFlag.get()
            if data[R.r[2]] == R.K[9]:
                Q_UAValidSF.put(data[R.r[3]])
            if data[R.r[2]] == R.K[10]:
                Q_Cont_TCPSend.put({R.r[0]: R.M[0], R.r[1]: R.H[4],
                                    R.r[2]: R.K[10], R.r[3]: data[R.r[3]]})


