import time
from App import Execution
from App import Resource


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
        Dict_1 = {}
        Dict_2 = {}
        DictAction_1 = {'ProcState': ['NovaStudio', False], 'ScreenState': ['Static', True]}
        DictAction_2 = {'ProcState': ['NovaStudio', True], 'ScreenState': ['Static', True]}
        DictAction_3 = {'ProcState': ['NovaStudio', True], 'ScreenState': ['Static', False]}
        DictAction_4 = {'ProcState': ['NovaStudio', False], 'ScreenState': ['Static', False]}
        DictAction_5 = {'ProcState': ['MarsServerProvider', False], }
        DictAction_6 = {'ProcState': ['MarsServerProvider', True], }
        while True:

            data = Q_in.get()
            # print('Execution', data, )
            if (data['key'] == 'ScreenState') or (data['key'] == 'ProcState' and data['data'][0] == 'NovaStudio' ):
                Dict_1[data['key']] = data['data']
                print(Dict_1)
                if Dict_1 == DictAction_1:
                    print('RunNova')
                    Dict_1 = {}
                if Dict_1 == DictAction_2:
                    print('RestartNova')
                    Dict_1 = {}
                if Dict_1 == DictAction_3:
                    print('NovaStudioOK')
                    Dict_1 = {}
                if Dict_1 == DictAction_4:
                    print('RebootSystem')
            if data['key'] == 'ProcState' and data['data'][0] == 'MarsServerProvider':
                Dict_2[data['key']] = data['data']
                print(Dict_2)
                if Dict_2 == DictAction_5:
                    print('TerminateMars')
                    Dict_2 = {}
                if Dict_2 == DictAction_6:
                    print('MarsTerminated')
                    Dict_2 = {}


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
        maxCountH = maxCount
        Dict = {}
        while True:
            data = Q_in.get()
            # print('Validation', module, 'data', data)
            if type(data) == dict:
                if data['data'][0] not in Dict:
                    Dict[data['data'][0]] = 0
                else:
                    pass
                checkCount += 1
                if data['data'][1] == checkValue:
                    Dict[data['data'][0]] += 1
                else:
                    pass
                # print('Validation', module, 'Dict', Dict )
                if Dict.__len__() > 1:
                    maxCountH = maxCount * Dict.__len__()
                else:
                    maxCountH = maxCount
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