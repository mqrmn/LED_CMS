
import re
import shutil
import psutil
import os
import config

import time
import sendMail
import logManager

def run():

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
                logManager.cmsLogger('Файл {} присутсвует'.format(pathTarget + fileName))

                try:
                    file = open(pathTarget + fileName, 'rb')
                    string = file.read()
                    isMatсh = re.search(search, str(string))
                except:
                    logManager.cmsLogger('В модуле validateNova возникла ошибка чтения файла {}'.format(time.ctime(), pathTarget + fileName))

                    x = 1

                if isMatсh == None:
                    logManager.cmsLogger('NovaStudio запущена корректно')

                else:
                    logManager.cmsLogger('NovaStudio некорректно запущена')

                    x = 1
                    novaProcess = psutil.Process(processPid['pid'])
                    for child in novaProcess.children(recursive=True):
                        child.kill()
                    novaProcess.kill()
                    logManager.cmsLogger('Процесс {} убит'.format(processName['name']))

            else:
                logManager.cmsLogger('отсутсвует файл {}'.format(time.ctime(), pathTarget + fileName))

                x = 1

        else:
            pass

    if x == 1:
        shutil.copy(pathSource + fileName, pathTarget + fileName)
        logManager.cmsLogger('Восстановление NovaStudio')

        try:
            sendMail.sendmail('{} NovaSudio была запущена некорректно. Запущено восстановление'.format(time.ctime()))
        except:
            pass
        logManager.cmsLogger('Перезагрузка системы')


        try:
            f = open('{}lastShutDown.txt'.format(config.tempPath, 'w'))
            f.write('1')
            f.close()
        except:
            pass


    return x5