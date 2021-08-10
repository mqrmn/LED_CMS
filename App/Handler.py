
import sys
sys.path.append("C:\\MOBILE\\Local\\CMS")

import time
from App import Action, Resource
import datetime

import os


# Обработчики очередей
class Queue:

    # Подготовка данных к отправке на сокет, метод условно резервный
    def SendController(self, Q_in, Q_out):
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

            if data == Resource.RunNova[1]:
                if ((datetime.datetime.now() - runNovaTime).seconds >= 30) or runNovaCount == 0:
                    print('TRUE', (datetime.datetime.now() - runNovaTime).seconds)
                    self.ToSend(data, Q_out)
                    runNovaTime = datetime.datetime.now()
                    runNovaCount += 1
                else:
                    print('FALSE', (datetime.datetime.now() - runNovaTime).seconds)
                data = None

            if data == Resource.TerminateNova:
                if ((datetime.datetime.now() - termNovaTime).seconds >= 30) or termNovaCount == 0:
                    print((datetime.datetime.now() - termNovaTime).seconds)
                    self.ToSend(data, Q_out)
                    termNovaTime = datetime.datetime.now()
                    termNovaCount += 1
                else:
                    pass
                    data = None
            if data == Resource.TerminateMars[1]:
                print('SendController', data)
                if ((datetime.datetime.now() - termMarsTime).seconds >= 30) or termMarsCount == 0:
                    self.ToSend(data, Q_out)
                    termMarsTime = datetime.datetime.now()
                    termMarsCount += 1
                else:
                    pass
                data = None
            if data == Resource.RestartNova[1]:
                if ((datetime.datetime.now() - resNovaTime).seconds >= 30) or resNovaCount == 0:
                    self.ToSend(data, Q_out)
                    resNovaTime = datetime.datetime.now()
                    resNovaCount += 1
                else:
                    pass
                data = None

            if data != None:
                self.ToSend(data, Q_out)


    # Обработчик очереди данных, приходящих от CMSUserAgent
    def FromUA(self, Q_in, Q_screenValidation, Q_procValidation, Q_Internal):
        while True:
            data = Q_in.get()
            lastReceive = datetime.datetime.now()
            if data['method'] == Resource.ComDict['method'][0]:
                if data['head'] == Resource.ComDict['head'][0]:
                    if data['key'] == Resource.ComDict['key'][0]:
                        Q_screenValidation.put({'key': data['key'], 'data': data['data'], })
                    if data['key'] == Resource.ComDict['key'][1]:
                        Q_procValidation.put({'key': data['key'], 'data': data['data'], })

            Q_Internal.put({Resource.root[1]: Resource.Head[2],
                            Resource.root[2]: Resource.Key[7],
                            Resource.root[3]: lastReceive, })


    # Подготавливает команты, отправляеемые на UA
    def CreateAction(self, Q_in, Q_out):
        DictNova = {}
        DictMars = {}
        command = None

        while True:
            data = Q_in.get()

            if (data['key'] == Resource.ComDict['key'][0]) \
                or (data['key'] == Resource.ComDict['key'][1] and data['data'][0] == Resource.ProcList[0]):
                DictNova[data['key']] = data['data']

                if DictNova == Resource.RunNova[0]:
                    command = Resource.RunNova[1]
                    DictNova = {}
                if DictNova == Resource.RestartNova[0]:
                    command = Resource.RestartNova[1]
                    DictNova = {}
                if command:
                    Q_out.put(command)
                    command = None
                    DictNova = {}

            if data['key'] == Resource.ComDict['key'][1] and data['data'][0] == Resource.ProcList[1]:
                DictMars[data['key']] = data['data']
                if DictMars == Resource.TerminateMars[0]:
                    command = Resource.TerminateMars[1]
                    DictMars = {}
                if command:
                    Q_out.put(command)
                    command = None
                    DictMars = {}

    # Обработчик данных, приходящих на UA
    def FromCore(self, Q_in, Q_out, ):
        while True:
            data = Q_in.get()
            print('FromCore', data)
            if data['method'] == Resource.ComDict['method'][0]:
                if data['head'] == Resource.ComDict['head'][1]:
                    Q_out.put(data)

    # Проверяет ключи в данных приходящих на UA, в соответсвии с ними запускает действия
    def UAAction(self, Q_in, Q_out,):
        _Execute_ = Action.Process()
        while True:

            data = Q_in.get()
            print('UAAction', data)
            if data['key'] == Resource.ComDict['key'][2]:
                _Execute_.Start(data['data'])
            if data['key'] == Resource.ComDict['key'][3]:
                _Execute_.Terminate(data['data'])
            if data['key'] == Resource.ComDict['key'][4]:
                _Execute_.Restart(data['data'])
            if data['key'] == Resource.ComDict['key'][5]:
                pass
            if data['key'] == Resource.ComDict['key'][6]:
                print('UAAction', data['key'], data['data'], )
                Q_out.put({'key': data['key'], 'data': data['data'], })

    # Проверяет поток приходящих данных на заданное соответсвие
    def Valid(self, Q_in, Q_out, checkValue, maxCount, head, sendAllCircles, ):
        checkCount, catchCount = 0, 0
        Dict = {}

        while True:
            data = Q_in.get()
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

    # Проверка списка процессов на соответсвие статусу активности
    def CheckProcList(self, Q_in, Q_out):
        while True:
            if Q_in.empty() == True:
                time.sleep(1)
            else:
                data = Q_in.get()
                if data[1] == Resource.ProcDict[data[0]]:
                    state = True
                else:
                    state = False
                Q_out.put({'key': Resource.Key[1], 'data': [data[0], state]})

    # Обработка очереди на отправку 
    def ToSend(self, data, Q_out):
        data['method'] = Resource.ComDict['method'][0]
        Q_out.put(data)

    # Обработка внутренней очереди
    def Internal(self, Q_in, Q_UAValid):
        while True:
            if Q_in.empty() != False:
                data = Q_in.get()
                if data[Resource.root[1]] == Resource.Head[2]:
                    if data[Resource.root[2]] == Resource.Key[7]:
                        Q_UAValid.put(data[Resource.root[3]])
                        print('Internal', data[Resource.root[3]])
            else:
                time.sleep(3)

