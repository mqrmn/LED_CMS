# 1.1.1

import sys
import win32pdh
import wmi

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import Resource

class Process:
    def GetProcessList(self):
        junk, list = win32pdh.EnumObjectItems(None, None, "Процесс", win32pdh.PERF_DETAIL_WIZARD)
        return list

    def GetProcessState(self, Q_out):
        processList = self.GetProcessList()
        for i in Resource.ProcDict:
            if i in processList:
                procState = True
            else:
                procState = False

            Q_out.put([i, procState])


    def GetService(self, name):
        pass
        c = wmi.WMI()
        for x in c.Win32_Service():
            if x.name == name:
                return x

    def StopService(self, name):
        self.GetService(name).StopService()

    def StartService(self, name):
        self.GetService(name).StartService()

    def RestartService(self):
        pass