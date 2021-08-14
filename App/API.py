# 1.1.1

import sys
import wmi
import os
import pythoncom
from inspect import currentframe, getframeinfo

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import Resource, LogManager

logging = LogManager._Log_Manager_()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])

class Win:
    def GetProcessState(self, Q_out):
        pythoncom.CoInitialize()
        handle = wmi.WMI()
        for i in Resource.ProcDict:
            proc = handle.Win32_Process(Name=i)
            if proc:
                procState = True
            else:
                procState = False
            Q_out.put([i, procState])

    def GetService(self, name):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        handle = wmi.WMI()
        if name:
            return handle.Win32_Service(name=name)[0]

    def StopService(self, name):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        return self.GetService(name).StopService()

    def StartService(self, name):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        return self.GetService(name).StartService()

    def GetServiceState(self, name):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        return self.GetService(name).State

    def RestartService(self):
        pass

    def RestartPC(self):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        handle = wmi.WMI(privileges=["Shutdown"])
        handle.Win32_OperatingSystem()[0].Reboot()
