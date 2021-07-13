
#v.1.1.1

import subprocess
import time
import psutil

from App import LogManager

import os
import App.Config.Config as Config
logging = LogManager._Log_Manager_()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])

class _ProcessManager_:

    def KillMars(self):
        popenSate = subprocess.Popen('C:\\Users\\rAdmin_local\\AppData\\Roaming\\Nova Star\\NovaLCT\\Bin\\NovaLCT.exe')
        time.sleep(120)
        novaKillState = 0
        while novaKillState == 0:
            for proc in psutil.process_iter():
                processName = proc.as_dict(attrs=['name'])
                processPid = proc.as_dict(attrs=['pid'])
                if processName['name'] == 'NovaLCT.exe':
                    novaProcess = psutil.Process(processPid['pid'])
                    for child in novaProcess.children(recursive=True):
                        child.kill()
                    novaProcess.kill()
                    novaKillState = 1
                else:
                    pass
                input()
                exit()

class StateManager:

    def Shutdown(self):
        for proc in psutil.process_iter():
            processName = proc.as_dict(attrs=['name'])
            processPid = proc.as_dict(attrs=['pid'])
            if processName['name'] == 'NovaStudio.exe':
                novaProcess = psutil.Process(processPid['pid'])
                for child in novaProcess.children(recursive=True):
                    child.kill()
                novaProcess.kill()
                break
            else:
                pass

        f = open('{}lastShutDown.txt'.format(Config.tempPath), 'w')
        f.write('1')
        f.close()

        os.system('shutdown /')