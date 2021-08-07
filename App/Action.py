
import sys
sys.path.append("C:\\MOBILE\\Local\\CMS")

import subprocess
import psutil
import time
from App import Resource, API

import wmi
import pythoncom



class Process:

    def Start(self, data):
        if data == Resource.ProcList[0]:
            self.RunNova()

    def Terminate(self, data):
        if data == Resource.ProcList[1]:
            self.TerminateMars()
        if data == Resource.ProcList[0]:
            self.TerminateNova()

    def Restart(self, data):
        if data == Resource.ProcList[0]:
            self.RestartNova()

    def RestartNova(self):
        self.TerminateNova()
        self.RunNova()

    def RunNova(self):
        pythoncom.CoInitialize()
        handle = wmi.WMI()
        handle.Win32_Process.Create(CommandLine='C:\\Program Files (x86)\\NovaStudio\\Bin\\NovaStudio.exe', )

    def TerminateNova(self):
        pythoncom.CoInitialize()
        handle = wmi.WMI()
        for proc in handle.Win32_Process(Name=Resource.ProcList[0]):
            proc.Terminate(Reason=1)



    def TerminateMars(self):
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

class Service:

    def Start(self):
        pass

    def Stop(self):
        pass

    def Restart(self):
        pass

class System:

    def Reboot(self):
        handle = API.Win()
        time.sleep(180)
        handle.RestartPC()