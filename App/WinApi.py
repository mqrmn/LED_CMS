# 1.1.1

import sys
import wmi
import pythoncom

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import Resource

class Process:

    def PutProcessStateToQ(self, Q_out):
        for i in Resource.ProcDict:
            procState = self.GetProcState()
            Q_out.put([i, procState])


    def GetProcState(self, procName):
        pythoncom.CoInitialize()
        handle = wmi.WMI()
        proc = handle.Win32_Process(Name=procName)
        if proc:
            procState = True
        else:
            procState = False

        return procState

    def GetService(self, name):
        handle = wmi.WMI()
        for x in handle.Win32_Service():
            if x.name == name:
                return x

    def StopService(self, name):
        self.GetService(name).StopService()

    def StartService(self, name):
        self.GetService(name).StartService()

    def RestartService(self):
        pass