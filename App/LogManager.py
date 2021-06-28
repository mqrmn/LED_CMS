#v.1.1.1

import logging.config
from App.Config import Config
from datetime import date
import time

class LogManager:

    def InitModule(self, module):

        logger = logging.getLogger(module)
        logging.basicConfig(level=logging.INFO)
        handler = logging.FileHandler('{}{}_{}.log'.format(Config.logPath, date.today(), module), encoding="UTF-8")
        logger.addHandler(handler)

        return(logger)


    def CMSLogger(self, module, method, string):
        module.info('{} {}: {}'.format(time.ctime(), method, string))

