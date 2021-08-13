# 1.1.1

import sys
import time
import pythoncom
import os
from inspect import currentframe, getframeinfo

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import Validation, Resource, File, API, Action, LogManager

logging = LogManager._Log_Manager_()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])
logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')


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

    def CMSUpdater(self, Q_out):
        C_Win = API.Win()
        C_FileMan = File.Manager()
        C_Action = Action.System()
        pythoncom.CoInitialize()
        while True:
            if C_FileMan.CMSUpgrade(False) == True:
                logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Обнаружено обновлние')
                time.sleep(180)
                stSvc = C_Win.StopService('CMS')
                if stSvc[0] == 0:
                    Q_out.put(True)
                    logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'CMS остановлена')
                    time.sleep(30)
                    C_FileMan.CMSUpgrade(True)
                    C_Action.Reboot()
                else:
                    logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Не удается остановить CMS, код: {}'.format(stSvc), )
            else:
                time.sleep(180)