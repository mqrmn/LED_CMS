
sc delete LMM	
sc stop CMS
sc delete CMS	

del /s /q "C:\Program Files\Python37"
rmdir /s /q "C:\Program Files\Python37"
del /s /q "C:\Users\rUser_local\AppData\Local\pip"
rmdir /s /q "C:\Users\rUser_local\AppData\Local\pip"

SCHTASKS /delete /TN "cmsKillMars"
SCHTASKS /delete /TN "cmsValidate"
SCHTASKS /delete /TN "cmsShutdown"

pause