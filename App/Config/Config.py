# v.1.1.1
from App.ConfigEx import ConfigEx

objType = ConfigEx.objType
objCode = ConfigEx.objCode
screenFormat = ConfigEx.screenFormat
objAddress = ConfigEx.objAddress
screenNum = ConfigEx.screen_num
regiondict = ConfigEx.regiondict

upgradePolitic = 1

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

timeoutSCheck = [10, 30]
timeoutPCheck = 30
# Настройка сокетов для внутренних коммуникаций
localhost = 'localhost'
CMSCoreInternalPort = 2203
CMSUserAgentPort = 2303



