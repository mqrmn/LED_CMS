encoding="UTF-8"

import sendMail
import time
import os
import config
import shutil
import logManager


class onRun:

    def lastShutdownValidation(self):

        # Считывает состояние последнего отключения
        f = open('{}lastShutDown.txt'.format(config.tempPath), 'r')
        lastShutDown = f.read()
        logManager.cmsLogger('lastShutDown = {}'.format(lastShutDown))
        f.close()

        # При некорректном состоянии отправляет e-mail
        # if lastShutDown == '0':
        #     sendMail.sendmail('{} предыдущее отключение было выполнено некорректно'.format(time.ctime()))


    def cmsRenew(self):
        yaListGroupRenew = os.listdir(config.groupCmsRenew)
        yaListLocalRenew = os.listdir(config.localCmsRenew)

        renewStatus = 0

        if yaListGroupRenew:
            renewStatus = 1
            for file in yaListGroupRenew:
                shutil.copy(config.groupCmsRenew + file, config.cmsLocalPath + file)
                logManager.cmsLogger('Обновление CMS из групповой папки: {}'.format(file))

        if yaListLocalRenew:
            renewStatus = 1
            for file in yaListLocalRenew:
                shutil.move(config.localCmsRenew + file, config.cmsLocalPath + file)
                logManager.cmsLogger('Обновление CMS из локальной папки: {}'.format(file))

        if renewStatus == 1:
            logManager.cmsLogger('Выполнено обновление CMS')
        else:
            logManager.cmsLogger('Нет файлов для обновления CMS')

    def validatePlayer(self):
        pass

    def defaultStatusCode(self):
        # Обнуляет код сотояния последнего отключения
        logManager.cmsLogger('2.1')
        f = open('{}lastShutDown.txt'.format(config.tempPath), 'w')
        f.write('0')
        f.close()
        logManager.cmsLogger('2.2')

        # Обнуляет код сотояния входа пользователя
        f = open('{}userState.txt'.format(config.tempPath), 'w')
        f.write('0')
        f.close()

        logManager.cmsLogger('2.3')

        # Обнуляет код сотояния экрнана
        f = open('{}screenState.txt'.format(config.tempPath), 'w')
        f.write('2')
        f.close()
