
import psutil
import os
import logManager
import config
import contentRefresh

def run():


    for proc in psutil.process_iter():
        processName = proc.as_dict(attrs=['name'])
        processPid = proc.as_dict(attrs=['pid'])
        if processName['name'] == 'NovaStudio.exe':
            novaProcess = psutil.Process(processPid['pid'])
            for child in novaProcess.children(recursive=True):
                child.kill()
            novaProcess.kill()
            logManager.cmsLogger('Процесс {} убит в контексте отключения системы по заданию cmsShutdown'.format(processName['name']))
            break
        else:
            pass
    try:
        f = open('{}lastShutDown.txt'.format(config.tempPath), 'w')
        f.write('1')
        f.close()
    except:
        logManager.cmsLogger('Не удалось обновить файл lastShutdown.txt при отключении')
        pass
    contentRefresh.run()

    logManager.cmsLogger('Завершение работы системы по заданию cmsShutdown')
    os.system('shutdown /s')

run()