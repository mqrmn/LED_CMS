# 1.1.1

import sys
import wmi
import pythoncom
import time
import psutil

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import Resource, LogManager

LOG = LogManager.Log_Manager()

class Win:

    handle = wmi.WMI()

    def CoinInit(self):
        pythoncom.CoInitialize()

    def GetWMI(self):
        self.CoinInit()
        handle = wmi.WMI()
        return handle

    def GetProcState(self, i):
        proc = self.GetWMI().Win32_Process(Name=i)
        return proc

    def GetProcessState(self, Q_out):
        for i in Resource.ProcDict:
            if self.GetProcState(i):
                procState = True
            else:
                procState = False
            Q_out.put([i, procState])


    def StartProc(self, executable):
        self.GetWMI().Win32_Process.Create(CommandLine=executable, )

    def TerminateProc(self, name):

        for proc in self.GetWMI().Win32_Process(Name=name):
            proc.Terminate(Reason=1)

    def GetService(self, name):
        LOG.CMSLogger('Called')
        handle = wmi.WMI()
        if name:
            return handle.Win32_Service(name=name)[0]

    def StopService(self, name):
        LOG.CMSLogger('Called')
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


class Nova(Win):

    def RestartNova(self):
        LOG.CMSLogger('Called')
        self.TerminateNova()
        self.RunNova()

    def RunNova(self):
        executable = 'C:\\Program Files (x86)\\NovaStudio\\Bin\\NovaStudio.exe'
        self.StartProc(executable)

    def TerminateNova(self):
        LOG.CMSLogger('Called')
        self.TerminateProc(Resource.ProcList[0])


    def TerminateMars(self):
        LOG.CMSLogger('Called')
        pythoncom.CoInitialize()
        handle = wmi.WMI()
        handle.Win32_Process.Create(
            CommandLine='C:\\Users\\rAdmin_local\\AppData\\Roaming\\Nova Star\\NovaLCT\\Bin\\NovaLCT.exe', )
        time.sleep(15)
        for proc in psutil.process_iter():
            processName = proc.as_dict(attrs=['name'])
            processPid = proc.as_dict(attrs=['pid'])
            if processName['name'] == 'NovaLCT.exe':

                novaProcess = psutil.Process(processPid['pid'])
                for child in novaProcess.children(recursive=True):
                    child.kill()

                novaProcess.kill()

            else:
                pass
