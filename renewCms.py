
import os
import config
import shutil
import logManager

def CMSRenew():

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
