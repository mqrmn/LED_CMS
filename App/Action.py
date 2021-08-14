# 1.1.1

import sys
import psutil
import time
import wmi
import pythoncom
import os
import shutil
from inspect import currentframe, getframeinfo
import re

sys.path.append("C:\\MOBILE\\Local\\CMS")
from App import Resource, API, LogManager

logging = LogManager._Log_Manager_()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])

class Process:

    def Start(self, data):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        if data == Resource.ProcList[0]:
            self.RunNova()

    def Terminate(self, data):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        if data == Resource.ProcList[1]:
            self.TerminateMars()
        if data == Resource.ProcList[0]:
            self.TerminateNova()

    def Restart(self, data):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        if data == Resource.ProcList[0]:
            self.RestartNova()

    def RestartNova(self):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        self.TerminateNova()
        self.RunNova()

    def RunNova(self):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        pythoncom.CoInitialize()
        handle = wmi.WMI()
        handle.Win32_Process.Create(CommandLine='C:\\Program Files (x86)\\NovaStudio\\Bin\\NovaStudio.exe', )

    def TerminateNova(self):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        pythoncom.CoInitialize()
        handle = wmi.WMI()
        for proc in handle.Win32_Process(Name=Resource.ProcList[0]):
            proc.Terminate(Reason=1)




    def TerminateMars(self):
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
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
        logging.CMSLogger(logHandler, getframeinfo(currentframe())[2], 'Called')
        handle = API.Win()
        time.sleep(180)
        handle.RestartPC()

class Files:
    def RestoreNovaBin(self):
        C_API = API.Win()
        if self.CheckNovaFile() == True:
            if C_API.GetProcState(Resource.ProcList[0]) == True:
                Process.TerminateNova()
                self.CopyNovaBin()


    def CheckNovaFile(self):
        file = open(Resource.novaBinFile, 'rb')
        string = file.read()
        return re.search('zh-CN', str(string))

    def CopyNovaBin(self):
        shutil.copy(Resource.novaBinFileBak,  Resource.novaBinFile)