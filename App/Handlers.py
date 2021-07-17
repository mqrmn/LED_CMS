import time
from App import Execution
from App import Resource
import json
import pickle
from App import Communicate

class _QHandler_:

    def PrepareToSend(self, Q_in, Q_out):
        while True:
            data = Q_in.get()
            data['method'] = 'put'
            Q_out.put(data)

    # Обработчик очереди данных, приходящих от CMSUserAgent
    def FromUserAgent(self, Q_in, Q_screenValidation, Q_procValidation):
        while True:
            data = Q_in.get()
            if data['method'] == 'put':
                if data['head'] == 'state':
                    if data['key'] == 'ScreenState':
                        Q_screenValidation.put( { 'key':data['key'], 'data':data['data'],} )
                    if data['key'] == 'ProcState':
                        Q_procValidation.put( { 'key':data['key'], 'data':data['data'],} )

    # Обработчик внутренней очереди
    def Internal(self, InternalQueue, ExecutionQueue):
        while True:
            data = InternalQueue.get()

    # Обработчик команд, отправляемых на CMSUserAgent
    def Execution(self, Q_in, Q_out):
        while True:
            data = Q_in.get()
            print('Execution', data, )
            # if type(data) == list:
            #     if data[0] == 'RunNovaStudio':
            #         if data[1] == True:
            #             Q_out.put(data)



    # Обработчик данных, приходящих на CMSUserAgent
    def FromCore(self, CMSCoreDataQueue):
        while True:
            if CMSCoreDataQueue.empty() == False:
                data = CMSCoreDataQueue.get()
                if type(data) == list:
                    if data[0] == 'RunNovaStudio':
                        if data[1] == True:
                            Execute_ = Execution._Execute_()
                            Execute_.RestartNovaStudio()
            else:
                pass

    # Обработчик - счетчик валидировочных очередей


    def Validation(self, Q_in, Q_out, checkValue, maxCount, head, sendAllCircles, module):
        checkCount, catchCount = 0, 0
        Dict = {}
        while True:
            data = Q_in.get()
            if type(data) == dict:
                if data['key'] == Resource.UAKey[1]:
                    maxCountH = maxCount * Resource.ProcessList.__len__()
                else:
                    maxCountH = maxCount
                if data['data'][0] not in Dict:
                    Dict[data['data'][0]] = 0
                else:
                    pass
                checkCount += 1
                if data['data'][1] == checkValue:
                    Dict[data['data'][0]] += 1
                else:
                    pass
                if checkCount >= maxCountH:
                    for i in Dict:
                        if Dict[i] == maxCount:
                            Q_out.put({'head': head, 'key': data['key'], 'data': [i, checkValue]})
                        else:
                            if sendAllCircles == True:
                                Q_out.put({'head': head, 'key': data['key'], 'data': [i, not checkValue]})
                            else:
                                pass
                    Dict = {}
                    checkCount, catchCount = 0, 0
                else:
                    pass

    def Validation_2(self, Q_in, Q_out, checkValue, maxCount, head, sendAllCircles, module):
        checkCount, catchCount = 0, 0
        maxCountH = maxCount
        Dict = {}
        while True:
            data = Q_in.get()
            if type(data) == dict:
                if Dict.__len__() > 1:
                    maxCountH = maxCount * Dict.__len__()
                else:
                    maxCountH = maxCount
                if data['data'][0] not in Dict:
                    Dict[data['data'][0]] = 0
                else:
                    pass
                checkCount += 1
                if data['data'][1] == checkValue:
                    Dict[data['data'][0]] += 1
                else:
                    pass
                if checkCount >= maxCountH:
                    for i in Dict:
                        if Dict[i] == maxCount:
                            Q_out.put({'head': head, 'key': data['key'], 'data': [i, checkValue]})
                        else:
                            if sendAllCircles == True:
                                Q_out.put({'head': head, 'key': data['key'], 'data': [i, not checkValue]})
                            else:
                                pass
                    Dict = {}
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
                Q_out.put({'key': Resource.UAKey[1], 'data': [data[0], state]})


    def StrToBool(self, D_in):
        D_out = None
        if D_in == 'True':
            D_out = True
        if D_in == 'False':
            D_out = False
        return D_out