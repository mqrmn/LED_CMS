# 1.1.1

import sys
import time
import pythoncom
import datetime
from inspect import currentframe, getframeinfo

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import Validation, Resource, File, API, Action, LogManager, Database

LOG = LogManager.Log_Manager()


class CMS:
    def Thread(self, Q_in, Q_out, data):
        while True:
            if Q_in.empty() == False:
                Q_data = Q_in.get()
                if Q_data == Resource.TerminateThread[0]:
                    break
            C_Valid = Validation.System()
            Th_States = C_Valid.Threads(data)
            if False in Th_States:
                pass
            time.sleep(10)

