# 1.1.1

import sys
import logging.config
import time
from datetime import date

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config

class _Log_Manager_:

    def InitModule(self, module):

        logger = logging.getLogger(module)
        logging.basicConfig(level=logging.INFO)
        handler = logging.FileHandler('{}{}_{}.log'.format(Config.logPath, date.today(), module), encoding="UTF-8")
        logger.addHandler(handler)

        return(logger)

    def CMSLogger(self, module, method, string):
        module.info('{} {}: {}'.format(time.ctime(), method, string))

