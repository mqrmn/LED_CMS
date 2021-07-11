pip install numpy

pip install opencv-python

pip install pywin32

pip install pyautogui

pip install psutil

copy "c:\Program Files\Python38\Lib\site-packages\pywin32_system32\pythoncom38.dll" "C:\program Files\Python38\Lib\site-packages\win32\pythoncom38.dlll"

copy "c:\Program Files\Python38\Lib\site-packages\pywin32_system32\pywintypes38.dll" "C:\program Files\Python38\Lib\site-packages\win32\pywintypes38.dll"

copy C:\MOBILE\YandexDisk\MACHINES\CMS_INIT C:\MOBILE\Local\CMS

TIMEOUT /T 1 /NOBREAK

SCHTASKS /Create /TN "cmsKillMars" /TR "'C:\Program Files\Python38\pythonw.exe' C:\MOBILE\Local\CMS\killMars.py" /RL HIGHEST /SC onlogon /DELAY 0005:00

TIMEOUT /T 1 /NOBREAK

SCHTASKS /Create /TN "cmsValidate" /TR "'C:\Program Files\Python38\pythonw.exe' C:\MOBILE\Local\CMS\cmsValidate.py" /SC onlogon

TIMEOUT /T 1 /NOBREAK

SCHTASKS /Create /TN "cmsShutdown" /TR "'C:\Program Files\Python38\pythonw.exe' C:\MOBILE\Local\CMS\shutDown.py" /SC daily /ST 22:00

TIMEOUT /T 1 /NOBREAK

SCHTASKS /run /TN "cmsKillMars"

TIMEOUT /T 1 /NOBREAK

SCHTASKS /run /TN "cmsValidate"

TIMEOUT /T 1 /NOBREAK

Python "C:\MOBILE\Local\CMS\App\CMSCore.py" --startup manual install

TIMEOUT /T 1 /NOBREAK

sc start cms

TIMEOUT /T 1 /NOBREAK

Python "C:\MOBILE\Local\CMS\firstContentRefresh.py"

pause