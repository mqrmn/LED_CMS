import time
from App import Execution
import win32pdh

class Handler:
    # Обработчик очереди данных, приходящих от CMSUserAgent
    def CMSUserAgentQueueHandler(self, CMSUserAgentQueue, ScreenValidationQueue):
        while True:
            if CMSUserAgentQueue.empty() == False:
                    data = CMSUserAgentQueue.get()
                    if type(data) == list:
                        if data[0] == 'CheckScreenValidation':
                            print('CMSUserAgentQueueHandler', data)
                            ScreenValidationQueue.put(data[1])
                        if data[0] == 'Что то другое':
                            pass
            else:
                time.sleep(5)

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
    def ValidationHandler(self, In_Queue, Out_Queue, okValue, maxCount, executionKey):
        checkCount, noValidCount = 0, 0
        while True:
            if In_Queue.empty() == True:
                time.sleep(1)
            else:
                if In_Queue.get() == okValue:
                    pass
                else:
                    noValidCount += 1
                checkCount += 1

                if checkCount >= maxCount:
                    if noValidCount == checkCount:
                        noValidCount = True
                    else:
                        noValidCount = False

                    Out_Queue.put([executionKey, noValidCount])

                    checkCount, noValidCount = 0, 0
                else:
                    pass

    def proclist(self):

            junk, instances = win32pdh.EnumObjectItems(None, None, None, win32pdh.PERF_DETAIL_WIZARD)
            return instances
