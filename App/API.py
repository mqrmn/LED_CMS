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

    def CoinInit(self):
        pythoncom.CoInitialize()

    def GetWMI(self, privileges=None):
        self.CoinInit()
        handle = wmi.WMI(privileges)
        return handle


class Process(Win):

    def GetProcState(self, i):
        return self.GetWMI().Win32_Process(Name=i)

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


class Service(Win):

    def GetService(self, name):
        LOG.CMSLogger('Called')
        if name:
            return self.GetWMI().Win32_Service(name=name)[0]

    def StopService(self, name):
        LOG.CMSLogger('Called')
        return self.GetService(name).StopService()

    def StartService(self, name):
        LOG.CMSLogger('Called')
        return self.GetService(name).StartService()

    def GetServiceState(self, name):
        LOG.CMSLogger( 'Called')
        return self.GetService(name).State


class System(Win):

    def RestartPC(self):
        LOG.CMSLogger('Called')
        self.GetWMI(privileges=["Shutdown"]).Win32_OperatingSystem()[0].RebootInit()




class Nova(Process):

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
        executable = 'C:\\Users\\rAdmin_local\\AppData\\Roaming\\Nova Star\\NovaLCT\\Bin\\NovaLCT.exe'
        self.StartProc(executable)

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
