
sc delete LMM

TIMEOUT /T 3 /NOBREAK

copy C:\MOBILE\YandexDisk\MACHINES\CMS_INIT C:\MOBILE\Local\CMS

TIMEOUT /T 3 /NOBREAK

SCHTASKS /Create /TN "cmsKillMars" /TR "'C:\Program Files\Python37\python.exe' C:\MOBILE\Local\CMS\killMars.py" /RL HIGHEST /SC onlogon /DELAY 0005:00

TIMEOUT /T 3 /NOBREAK

SCHTASKS /Create /TN "cmsValidate" /TR "'C:\Program Files\Python37\python.exe' C:\MOBILE\Local\CMS\cmsValidate.py" /SC onlogon

TIMEOUT /T 3 /NOBREAK

SCHTASKS /Create /TN "cmsShutdown" /TR "'C:\Program Files\Python37\python.exe' C:\MOBILE\Local\CMS\shutDown.py" /SC daily /ST 22:00

TIMEOUT /T 3 /NOBREAK

SCHTASKS /run /TN "cmsKillMars"

TIMEOUT /T 3 /NOBREAK

SCHTASKS /run /TN "cmsValidate"

TIMEOUT /T 3 /NOBREAK

Python "C:\MOBILE\Local\CMS\cmsService.py" --startup auto install

TIMEOUT /T 3 /NOBREAK

sc start cms

TIMEOUT /T 3 /NOBREAK

Python "C:\MOBILE\Local\CMS\firstContentRefresh.py"

pause