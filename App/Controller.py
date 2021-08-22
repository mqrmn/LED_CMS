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

    def CMSUpdater(self, Q_out):
        C_Win = API.Win()
        C_FileMan = File.Manager()
        C_Action = Action.System()
        pythoncom.CoInitialize()
        while True:
            if C_FileMan.CMSUpgrade(False) == True:
                LOG.CMSLogger('Обнаружено обновление')
                time.sleep(180)
                stSvc = C_Win.StopService('CMS')
                if stSvc[0] == 0:
                    Q_out.put(True)
                    LOG.CMSLogger( 'CMS остановлена')
                    time.sleep(30)
                    C_FileMan.CMSUpgrade(True)
                    table = Database.Tables()
                    table.SelfInitShutdown.create(trigger=getframeinfo(currentframe())[2],
                                                  key='reboot',
                                                  datetime=datetime.datetime.now(), )

                    C_Action.RebootInit()
                else:
                    LOG.CMSLogger(
                                      'Не удается остановить CMS, код: {}'.format(stSvc), )
            else:
                time.sleep(1800)


