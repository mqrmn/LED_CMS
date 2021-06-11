encoding="UTF-8"

import configEx



objType = configEx.objType
objCode = configEx.objCode
screenFormat = configEx.screenFormat
objAddress = configEx.objAddress
screenNum = configEx.screen_num
regiondict = configEx.regiondict

# Установка путей

# Настройка корневых директорий
#workpath = '{}\\temp\\'.format(os.path.abspath(os.path.dirname(__file__)))
workPath = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\{}\\'.format(objType, objCode)
logPath = '{}Log\\'.format(workPath)
tempPath = '{}Temp\\'.format(workPath)
#targetPath = '{}\\Content\\'.format(workPath)
cmsConfigPath = '{}Config\\'.format(workPath)

# Настройка локальных директорий
configTargetPath = 'C:\\MOBILE\\Local\\Config\\'
cmsLocalPath = 'C:\\MOBILE\\Local\\CMS\\'

# Настройка директорий обновления контента
yaFilesUnex = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\Content\\'.format(objType)
yaFilesEx = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\{}\\Content\\'.format(objType, objCode)
yaFilesExcept = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\{}\\Content.Except\\'.format(objType, objCode)
localFilesUnex = 'C:\\MOBILE\\Local\\Content\\Unex\\'
localFilesEx = 'C:\\MOBILE\\Local\\Content\\Ex\\'

# Настройка директорий обновлений CMS
globalCmsRenew = 'C:\\MOBILE\\YandexDisk\\MACHINES\\CMS\\'
groupCmsRenew = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\CMS\\'.format(objType)
localCmsRenew = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\{}\\CMS\\'.format(objType, objCode)



