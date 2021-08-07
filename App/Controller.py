
import sys
sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import Validation, Resource
import time

import os


class CMS:
    def Thread(self, Q_in, Q_out, data):
        while True:
            if Q_in.empty() == False:
                Q_data = Q_in.get()
                if Q_data == Resource.TerminateThread[0]:
                    break
            C_Valid = Validation._System_()
            Th_States = C_Valid.Threads(data)
            if False in Th_States:
                pass
            time.sleep(10)