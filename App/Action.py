import subprocess
import psutil
import time
from App import Resource


class Process:

    def Start(self, data):
        if data == Resource.ProcList[0]:
            self.RunNova()

    def Terminate(self, data):
        if data == Resource.ProcList[1]:
            self.TerminateMars()

    def Restart(self, data):
        if data == Resource.ProcList[0]:
            self.RestartNova()

    def RestartNova(self):
        self.TerminateNova()
        self.RunNova()

    def RunNova(self):
        subprocess.Popen('C:\\Program Files (x86)\\Nova Star\\NovaStudio\\Bin\\NovaStudio.exe')

    def TerminateNova(self):
        print('TerminateNovaStudio')
        for proc in psutil.process_iter():
            processName = proc.as_dict(attrs=['name'])
            processPid = proc.as_dict(attrs=['pid'])
            if processName['name'] == 'NovaStudio.exe':
                novaProcess = psutil.Process(processPid['pid'])
                for child in novaProcess.children(recursive=True):
                    child.kill()
                novaProcess.kill()
            else:
                pass

    def TerminateMars(self):
        popenState = subprocess.Popen('C:\\Users\\rAdmin_local\\AppData\\Roaming\\Nova Star\\NovaLCT\\Bin\\NovaLCT.exe')
        time.sleep(30)

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

