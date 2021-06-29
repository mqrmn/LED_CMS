#v.1.1.1

import re
import shutil
import psutil
from App.Config import Config
import os

class System:

    def LastShutdown(self):
        f = open('{}lastShutDown.txt'.format(Config.tempPath), 'r')
        lastShutDown = f.read()
        f.close()

    def NovaStudio(self):
        pathTarget = 'C:\\Users\\rUser_local\\AppData\\Roaming\\NovaStudio2012\\'
        pathSource = 'C:\\Users\\rUser_local\\AppData\\Roaming\\NovaStudio2012_bcp\\'
        fileName = 'sysinfo.bin'
        search = 'zh-CN'
        x = 0
        x5 = 0
        for proc in psutil.process_iter():
            processName = proc.as_dict(attrs=['name'])
            processPid = proc.as_dict(attrs=['pid'])
            if processName['name'] == 'NovaStudio.exe':
                x5 = 1
                isNovaBin = os.path.exists(pathTarget + fileName)
                if isNovaBin == True:
                    try:
                        file = open(pathTarget + fileName, 'rb')
                        string = file.read()
                        isMatсh = re.search(search, str(string))
                    except:

                        x = 1
                    if isMatсh == None:
                        pass
                    else:
                        x = 1
                        novaProcess = psutil.Process(processPid['pid'])
                        for child in novaProcess.children(recursive=True):
                            child.kill()
                        novaProcess.kill()
                else:
                    x = 1
            else:
                pass
        if x == 1:
            shutil.copy(pathSource + fileName, pathTarget + fileName)
            try:
                pass
            except:
                pass
            try:
                f = open('{}lastShutDown.txt'.format(Config.tempPath, 'w'))
                f.write('1')
                f.close()
            except:
                pass
        return x5
