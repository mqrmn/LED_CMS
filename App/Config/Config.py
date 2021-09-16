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

# Setting up root directories
workPath = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\{}\\'.format(objType, objCode)
logPath = '{}Log\\'.format(workPath)

# Setting up local directories
configTargetPath = 'C:\\MOBILE\\Local\\Config\\'
CMSArchPath = 'C:\\MOBILE\\Local\\Arch\\'

# Configuring content update directories
yaFilesUnex = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\Content\\'.format(objType)
yaFilesEx = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\{}\\Content\\'.format(objType, objCode)
yaFilesExcept = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\{}\\Content.Except\\'.format(objType, objCode)
localFilesUnex = 'C:\\MOBILE\\Local\\Content\\Unex\\'
localFilesEx = 'C:\\MOBILE\\Local\\Content\\Ex\\'

# Setting up CMS update directories
globalCmsRenew = 'C:\\MOBILE\\YandexDisk\\MACHINES\\CMS_DEV\\'
groupCmsRenew = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\CMS_DEV\\'.format(objType)
localCmsRenew = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\{}\\CMS\\'.format(objType, objCode)

# Database placement
DBFolder = 'C:\\MOBILE\\Local\\CMS\\Database\\'
DBFile = 'CMS.db'
DBPath = DBFolder + DBFile

# Placing NovaBin
novaBinFolder = 'C:\\Users\\rUser_local\\AppData\\Roaming\\NovaStudio2012\\'
novaBinFileBak = novaBinFolder + 'sysInfo.bin.bak'
novaBinFile = novaBinFolder + 'sysInfo.bin'

# Setting timeouts
timeoutSCheck = [10, 30]
timeoutPCheck = 30

# Setting up sockets for internal communications
localhost = '127.0.0.1'
CMSCoreInternalPort = 22031
CMSUserAgentPort = 23032
CMSControllertPort = 24033

# Mail Config

smtpSender = 'salon.notification@znp74.ru'
smtpPass = '6M3QP8LKKsesZg'
smtpReceiver = 'alex.s@znp74.ru'
smtpServer = 'smtp.yandex.ru'
smtpPort = 587

# Timeouts
# Handler.Queue.SendController
runNovaTimeout = 5
terminateNovaTimeout = 5
terminateMarsTimeout = 30
restartNovaTimeout = 500
# Handler.Queue.CreateAction
restartNovaMaxCount = 3
restoreNovaMaxCount = 3
