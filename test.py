import logManager
import config
import os
import time
from datetime import date

userState = '0'
# количество итераций цикла с отсутсвием движения экрана
scrFreezCount = 0
# количество итераций цикла с отсутсвием запуска валидатора
scrNotRunCount = 0
# Статус запуска плеера
isNovaRun = 0
# Статус запуска валидатора экрана
isScrRun = '0'
d = date.today()

userNotLoggedInCount = 0

while True:
    # ПРОВЕРКА ВХОЖДЕНИЯ ПОЛЬЗОВАТЕЛЯ
    if userState == '0':
        logManager.cmsLogger('2')
        f = open('{}userState.txt'.format(config.tempPath), 'r')
        userState = f.read()
        f.close()
        userNotLoggedInCount += 1
        if userNotLoggedInCount > 30:
            userNotLoggedInCount = 0
        if (userState == '1'):
            userNotLoggedInCount = 0
        logManager.cmsLogger('3')

    else:
        # Проверяет состояние экрана
        isStateFile = os.path.exists('{}screenState.txt'.format(config.tempPath))
        if isStateFile == True:
            f = open('{}screenState.txt'.format(config.tempPath), 'r')
            screenState = f.read()
            f.close()
            if screenState == '0':
                scrFreezCount = 0
            if screenState == '2':
                scrNotRunCount += 1
                if scrNotRunCount >= 40:
                    scrNotRunCount = 0
            else:
                scrFreezCount += 1
                if scrFreezCount >= 45:
                    scrFreezCount = 0
            logManager.cmsLogger('4')

        else:
            pass

    time.sleep(10)
