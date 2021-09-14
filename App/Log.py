# 1.1.1

import sys
import logging.config
import time
from datetime import date
from inspect import currentframe, getframeinfo, getmodulename

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config


class LogManager:

    @staticmethod
    def init_module(module):

        logger = logging.getLogger(module)
        logging.basicConfig(level=logging.INFO)
        handler = logging.FileHandler('{}{}_{}.log'.format(Config.logPath, date.today(), module), encoding="UTF-8")
        if logger.hasHandlers():
            logger.handlers.clear()
        logger.addHandler(handler)

        return logger

    def cms_logger(self, string):

        frame = getframeinfo(currentframe().f_back)
        logger = self.init_module(getmodulename(frame.filename))

        logger.info('{} {}: {}'.format(time.ctime(), frame.function, string))
