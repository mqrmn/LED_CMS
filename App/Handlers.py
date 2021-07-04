import time

class Handler:
    def CMSUserAgentQueueHandler(self, CMSUserAgentQueue, ScreenValidationQueue):
        while True:
            if CMSUserAgentQueue.empty() == True:
                time.sleep(5)
            else:
                data = CMSUserAgentQueue.get()
                if type(data) == list:
                    if data[0] == 'CheckScreenValidation':
                        ScreenValidationQueue.put(data[1])
                else:
                    print(type(data))