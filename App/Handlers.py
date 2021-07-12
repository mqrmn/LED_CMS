import time
from App import Execution
import win32pdh

class Handler:
    # Обработчик очереди данных, приходящих от CMSUserAgent
    def CMSUserAgentQueueHandler(self, Q_in, Q_screenValidation):
        while True:
            if Q_in.empty() == False:
                    data = Q_in.get()
                    print('CMSUserAgentQueueHandler', data)
                    if type(data) == list:
                        if data[0] == 'CheckScreenValidation':
                            if data[1] == 'True':
                                data.append(True)
                            if data[1] == 'False':
                                data.append(False)
                            Q_screenValidation.put(data[2])
            else:
                time.sleep(1)

    # Обработчик внутренней очереди
    def InternalQueueHandler(self, InternalQueue, ExecutionQueue):
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
    def ExecutionQueueHandler(self, ExecutionQueue, SendUserAgentQueue):
        while True:
            if ExecutionQueue.empty() == False:
                data = ExecutionQueue.get()
                print('ExecutionQueueHandler 0', data)
                if type(data) == list:
                    if data[0] == 'CoreScreenValidation':
                        if data[1] == True:
                            print('ExecutionQueueHandler', data)
                            SendUserAgentQueue.put(data)
            else:
                pass

    # Обработчик данных, приходящих на CMSUserAgent
    def CMSCoreDataQueueHandler(self, CMSCoreDataQueue):
        while True:
            if CMSCoreDataQueue.empty() == False:
                data = CMSCoreDataQueue.get()
                if type(data) == list:
                    if data[0] == 'CoreScreenValidation':
                        if data[1] == True:
                            Execute_ = Execution.Execute()
                            print('CMSCoreDataQueue', data)
                            Execute_.RestartNovaStudio()
            else:
                pass

    # Обработчик - счетчик валидировочных очередей
    def ValidationHandler(self, Q_in, Q_out, checkValue, maxCount, executionKey, sendAllCircles, x):
        checkCount, catchCount = 0, 0
        while True:

            if Q_in.empty() == True:
                time.sleep(1)
            else:
                data = Q_in.get()
                print('----------ValidationHandler', x, 'data', data, type(data))
                if data == checkValue:
                    catchCount += 1
                else:
                    pass
                checkCount += 1
                print(x, checkCount, catchCount)
                if checkCount >= maxCount:
                    if catchCount == checkCount:
                        print('----------ValidationHandler', x, True)
                        Q_out.put([executionKey, True])
                    else:
                        print('----------ValidationHandler', x, False)
                        if sendAllCircles == True:
                            Q_out.put([executionKey, False])
                        else:
                            pass
                    checkCount, catchCount = 0, 0
                else:
                    pass

    def proclist(self):

            junk, instances = win32pdh.EnumObjectItems(None, None, None, win32pdh.PERF_DETAIL_WIZARD)
            return instances
