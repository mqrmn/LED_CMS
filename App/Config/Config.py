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
globalCmsRenew = 'C:\\MOBILE\\YandexDisk\\MACHINES\\CMS\\App\\'
groupCmsRenew = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\CMS\\App\\'.format(objType)
localCmsRenew = 'C:\\MOBILE\\YandexDisk\\MACHINES\\{}\\{}\\CMS\\App\\'.format(objType, objCode)

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

smtpSender = ''
smtpPass = ''
smtpReceiver = ''
smtpServer = ''
smtpPort = 587

# Timeouts & counts
# Handler.Queue.SendController
runNovaTimeout = 5
terminateNovaTimeout = 5
terminateMarsTimeout = 30
restartNovaTimeout = 500
# Handler.Queue.CreateAction
restartNovaMaxCount = 3
restoreNovaMaxCount = 3
# UserAgent.CMSUserAgent
ua_check_screen_count = 2
ua_check_proc_count = 1

# CMSCore
core_check_screen_count = 3
core_check_proc_count = 3

# Control.
# scheduler
shutdown_time = '21:55'
# ua_valid
ua_delay = 300
# cms_service
cms_service_delay = 60
cont_last_reb_delay = 300
# power_manager
last_reb_delay = 300

# File.
# CMSUpdate.
# cms_updater
cms_updater_delay1 = 180
cms_updater_delay2 = 300
cms_updater_delay3 = 1800
# RenewContent.
# dynamic_renew_cont
count_pass = 5
dynamic_renew_cont_delay = 500
# content_renew_handle
content_renew_handle_delay = 20

# Act.
# System.
pre_reboot_delay = 180
pre_shutdown_delay = 180

