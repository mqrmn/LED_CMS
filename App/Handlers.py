import time

class Handler:

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

    def ExecutionQueueHandler(self, ExecutionQueue, SendUserAgentQueue):
        while True:
            if ExecutionQueue.empty() == False:
                data = ExecutionQueue.get()
                print('ExecutionQueueHandler 0', data)
                if type(data) == list:
                    if data[0] == 'CoreScreenValidation':
                        if data[1] == '1':
                            print('ExecutionQueueHandler', data)
                            SendUserAgentQueue.put(data)
            else:
                pass

    def CMSCoreDataQueueHandler(self, CMSCoreDataQueue):
        while True:
            if CMSCoreDataQueue.empty() == False:
                data = CMSCoreDataQueue.get()
                if type(data) == list:
                    if data[0] == 'CoreScreenValidation':
                        if data[1] == '1':
                            print('CMSCoreDataQueue', data)
            else:
                pass