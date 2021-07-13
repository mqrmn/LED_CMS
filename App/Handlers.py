import time
from App import Execution
from App import Resource
import win32pdh

class _QHandler_:
    # Обработчик очереди данных, приходящих от CMSUserAgent
    def FromUserAgent(self, Q_in, Q_screenValidation, Q_procValidation):
        while True:
            data = Q_in.get()
            # print('FromUserAgent', data)
            if data[0] == 'CheckScreenValidation':
                Q_screenValidation.put(self.StrToBool(data[1]))
            if data[0] in Resource.ProcessList:
                Q_procValidation.put([data[0], self.StrToBool(data[1])])

    # Обработчик внутренней очереди
    def Internal(self, InternalQueue, ExecutionQueue):
        while True:
            if InternalQueue.empty() == False:
                data = InternalQueue.get()
                if type(data) == list:
                    if data[0] == 'CoreScreenValidation':
                        if data[1] == '1':
                            pass
            else:
                pass
    # Обработчик команд, отправляемых на CMSUserAgent
    def Execution(self, ExecutionQueue, SendUserAgentQueue):
        while True:
            if ExecutionQueue.empty() == False:
                data = ExecutionQueue.get()
                print('Execution', data)
                if type(data) == list:
                    if data[0] == 'CoreScreenValidation':
                        if data[1] == True:
                            SendUserAgentQueue.put(data)
            else:
                pass

    # Обработчик данных, приходящих на CMSUserAgent
    def FromCore(self, CMSCoreDataQueue):
        while True:
            if CMSCoreDataQueue.empty() == False:
                data = CMSCoreDataQueue.get()
                if type(data) == list:
                    if data[0] == 'CoreScreenValidation':
                        if data[1] == True:
                            Execute_ = Execution._Execute_()
                            Execute_.RestartNovaStudio()
            else:
                pass

    # Обработчик - счетчик валидировочных очередей
    def Validation(self, Q_in, Q_out, checkValue, maxCount, executionKey, sendAllCircles, module):
        checkCount, catchCount = 0, 0
        dict = {}
        if executionKey == None:
            executionKeyIsNone = True
        else:
            executionKeyIsNone = False

        while True:
            data = Q_in.get()
            if type(data) == list:
                if data[0] not in dict:
                    dict[data[0]] = 0
                else:
                    pass
                checkCount += 1
                if data[1] == checkValue:
                    dict[data[0]] += 1
                else:
                    pass
                if checkCount >= maxCount*Resource.ProcessList.__len__():
                    for i in dict:
                        if executionKeyIsNone == True:
                            executionKey = i
                        else:
                            pass
                        if dict[i] == checkCount/Resource.ProcessList.__len__():
                            Q_out.put([executionKey, True])
                        else:
                            if sendAllCircles == True:
                                Q_out.put([executionKey, False])
                            else:
                                pass
                    dict = {}
                    checkCount, catchCount = 0, 0
                else:
                    pass
            else:
                checkCount += 1
                if data == checkValue:
                    catchCount += 1
                else:
                    pass

                if checkCount >= maxCount:
                    if catchCount == checkCount:
                        Q_out.put([executionKey, True])
                    else:
                        if sendAllCircles == True:
                            Q_out.put([executionKey, False])
                        else:
                            pass
                    checkCount, catchCount = 0, 0
                else:
                    pass

    def CheckProcList(self, Q_in, Q_out):
        while True:
            if Q_in.empty() == True:
                time.sleep(1)
            else:
                data = Q_in.get()
                if data[1] == Resource.ProcessList[data[0]]:
                    state = True
                else:
                    state = False
                # print('CheckProcList', [data[0], state])
                Q_out.put([data[0], state])

    def StrToBool(self, D_in):
        D_out = None
        if D_in == 'True':
            D_out = True
        if D_in == 'False':
            D_out = False
        return D_out