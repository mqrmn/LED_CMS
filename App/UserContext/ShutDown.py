#v.1.1.1

import psutil
import os
from App import LogManager, ContentRefresh
from App.Config import Config


def run():


    for proc in psutil.process_iter():
        processName = proc.as_dict(attrs=['name'])
        processPid = proc.as_dict(attrs=['pid'])
        if processName['name'] == 'NovaStudio.exe':
            novaProcess = psutil.Process(processPid['pid'])
            for child in novaProcess.children(recursive=True):
                child.kill()
            novaProcess.kill()
            LogManager.cmsLogger('Процесс {} убит в контексте отключения системы по заданию cmsShutdown'.format(processName['name']))
            break
        else:
            pass
    try:
        f = open('{}lastShutDown.txt'.format(Config.tempPath), 'w')
        f.write('1')
        f.close()
    except:
        LogManager.cmsLogger('Не удалось обновить файл lastShutdown.txt при отключении')
        pass
    ContentRefresh.run()

    LogManager.cmsLogger('Завершение работы системы по заданию cmsShutdown')
    os.system('shutdown /s')

run()