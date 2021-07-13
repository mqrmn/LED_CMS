import subprocess
import psutil
import time

class _Execute_:
    def RestartNovaStudio(self):

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
        popenState = subprocess.Popen('C:\\Program Files (x86)\\Nova Star\\NovaStudio\\Bin\\NovaStudio.exe')

    def KillMars(self):
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
