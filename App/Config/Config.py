# v.1.1.1

import sys

sys.path.append("C:\\MOBILE\\Local\\CMS")
from ConfigEx import ConfigEx


objType = ConfigEx.objType
objCode = ConfigEx.objCode
screenFormat = ConfigEx.screenFormat
objAddress = ConfigEx.objAddress
screenNum = ConfigEx.screen_num
regiondict = ConfigEx.regiondict

upgradePolitic = 1

# Настройка корневых директорий
workPath = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\{}\\'.format(objType, objCode)
logPath = '{}Log\\'.format(workPath)

# Настройка локальных директорий
configTargetPath = 'C:\\MOBILE\\Local\\Config\\'
CMSArchPath = 'C:\\MOBILE\\Local\\Arch\\'

# Настройка директорий обновления контента
yaFilesUnex = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\Content\\'.format(objType)
yaFilesEx = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\{}\\Content\\'.format(objType, objCode)
yaFilesExcept = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\{}\\Content.Except\\'.format(objType, objCode)
localFilesUnex = 'C:\\MOBILE\\Local\\Content\\Unex\\'
localFilesEx = 'C:\\MOBILE\\Local\\Content\\Ex\\'

# Настройка директорий обновлений CMS
globalCmsRenew = 'C:\\MOBILE\\YandexDisk\\MACHINES\\CMS_DEV\\'
groupCmsRenew = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\CMS_DEV\\'.format(objType)
localCmsRenew = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\{}\\CMS\\'.format(objType, objCode)

DBFolder = 'C:\\MOBILE\\Local\\CMS\\Database\\'
DBFile = 'CMS.db'
DBPath = DBFolder + DBFile


timeoutSCheck = [10, 30]

# Настройка сокетов для внутренних коммуникаций
localhost = 'localhost'
CMSCoreInternalPort = 2203
CMSUserAgentPort = 2303
CMSControllertPort = 2403


