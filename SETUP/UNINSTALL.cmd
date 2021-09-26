
sc delete LMM	
sc stop CMS
sc delete CMS

SCHTASKS /delete /TN "cmsKillMars"
SCHTASKS /delete /TN "cmsValidate"
SCHTASKS /delete /TN "cmsShutdown"

pause