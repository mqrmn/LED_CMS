pip install numpy
pip install opencv-python
pip install pywin32
pip install pyautogui
pip install psutil
pip install socket
pip install schedule
pip install wmi
pip install peewee

copy "c:\Program Files\Python38\Lib\site-packages\pywin32_system32\pythoncom38.dll" "C:\program Files\Python38\Lib\site-packages\win32\pythoncom38.dlll"
copy "c:\Program Files\Python38\Lib\site-packages\pywin32_system32\pywintypes38.dll" "C:\program Files\Python38\Lib\site-packages\win32\pywintypes38.dll"

copy C:\MOBILE\YandexDisk\MACHINES\CMS_INIT C:\MOBILE\Local\CMS

SCHTASKS /Create /TN "CMSUserAgent" /TR "'C:\Program Files\Python38\pythonw.exe' C:\MOBILE\Local\CMS\CMSUserAgent.py" /RL HIGHEST /SC onlogon /DELAY 0005:00
Python "C:\MOBILE\Local\CMS\App\CMSCore.py" --startup auto install
Python "C:\MOBILE\Local\CMS\App\Controller\CMSController.py" --startup auto install

sc start CMSController
sc start CMS
SCHTASKS /run /TN "CMSUserAgent"

pause