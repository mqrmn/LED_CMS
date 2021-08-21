# 1.1.1

import sys
import logging.config
import time
from datetime import date
from inspect import currentframe, getframeinfo, getmodulename

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config

class Log_Manager:

    def InitModule(self, module):

        logger = logging.getLogger(module)
        logging.basicConfig(level=logging.INFO)
        handler = logging.FileHandler('{}{}_{}.log'.format(Config.logPath, date.today(), module), encoding="UTF-8")
        logger.addHandler(handler)

        return(logger)

    def CMSLogger(self, string):


        frame = getframeinfo(currentframe().f_back)
        logger = self.InitModule(getmodulename(frame.filename))

        logger.info('{} {}: {}'.format(time.ctime(), frame.function, string))

