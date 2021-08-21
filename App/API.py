# 1.1.1

import sys
import wmi
import pythoncom

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import Resource, LogManager

LOG = LogManager.Log_Manager()

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
        LOG.CMSLogger('Called')
        handle = wmi.WMI()
        if name:
            return handle.Win32_Service(name=name)[0]

    def StopService(self, name):
        LOG.CMSLogger( 'Called')
        return self.GetService(name).StopService()

    def StartService(self, name):
        LOG.CMSLogger('Called')
        return self.GetService(name).StartService()

    def GetServiceState(self, name):
        LOG.CMSLogger( 'Called')
        return self.GetService(name).State

    def RestartService(self):
        pass

    def RestartPC(self):
        LOG.CMSLogger('Called')
        handle = wmi.WMI(privileges=["Shutdown"])
        handle.Win32_OperatingSystem()[0].Reboot()
