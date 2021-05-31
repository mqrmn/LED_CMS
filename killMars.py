encoding="UTF-8"

import subprocess
import time
import psutil

import logManager

def run():


    logManager.cmsLogger('Запущен killMars')

    popenSate = subprocess.Popen('C:\\Users\\rAdmin_local\\AppData\\Roaming\\Nova Star\\NovaLCT\\Bin\\NovaLCT.exe')
    logManager.cmsLogger('статус запуска NovaLCT: {}'.format(popenSate))

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
                        logManager.cmsLogger('Процесс {} остановлен'.format(child))
                    novaProcess.kill()
                    logManager.cmsLogger('Процесс {} остановлен'.format(processName['name']))
                    novaKillState = 1
                else:
                    pass
            except:
                logManager.cmsLogger('В модуле killMars возникла ошибка')

        if novaKillState == 0:
            logManager.cmsLogger('Процесс NovaLCT.exe не найден. Повторный запуск')

        else:
            logManager.cmsLogger('Процесс NovaLCT.exe успешно завершен')
            input()
            exit()


run()

