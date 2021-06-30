#v.1.1.1

import subprocess
import time
import psutil

from App import LogManager

import os

logging = LogManager.LogManager()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])

def run():


    LogManager.cmsLogger('Запущен killMars')

    popenSate = subprocess.Popen('C:\\Users\\rAdmin_local\\AppData\\Roaming\\Nova Star\\NovaLCT\\Bin\\NovaLCT.exe')
    LogManager.cmsLogger('статус запуска NovaLCT: {}'.format(popenSate))

    time.sleep(120)

    novaKillState = 0
    
    while  novaKillState == 0:
        for proc in psutil.process_iter():
            try:
                processName = proc.as_dict(attrs=['name'])
                processPid = proc.as_dict(attrs=['pid'])
                if processName['name'] == 'NovaLCT.exe':

                    novaProcess = psutil.Process(processPid['pid'])
                    for child in novaProcess.children(recursive=True):
                        child.kill()
                        LogManager.cmsLogger('Процесс {} остановлен'.format(child))
                    novaProcess.kill()
                    LogManager.cmsLogger('Процесс {} остановлен'.format(processName['name']))
                    novaKillState = 1
                else:
                    pass
            except:
                LogManager.cmsLogger('В модуле killMars возникла ошибка')

        if novaKillState == 0:
            LogManager.cmsLogger('Процесс NovaLCT.exe не найден. Повторный запуск')

        else:
            LogManager.cmsLogger('Процесс NovaLCT.exe успешно завершен')
            input()
            exit()


run()

