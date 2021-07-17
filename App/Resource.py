


NovaFileKey = {'Backup', 'Restore', }
ActionKey = ['RunNova', 'RestartNova', 'TerminateNova', 'RestartSystem', ]
ScreenKey = ['ScreenIsStatic', ]
stateKey = [['ScreenState', ['ScreenIsStatic', ], ], ['ProcessState', ['NovaStudio', 'MarsServerProvider', ], ], ]

#---------
ProcessList = {'NovaStudio': True, 'MarsServerProvider': False, }
ScreenState = ['Static', ]
ProcState = [True, False]


UAMethod = ['put', 'get', ]
UAhead = ['State', 'Action', ]
UAKey = ['ScreenState', 'ProcState', ]
UADict = {'method': UAMethod, 'head': UAhead, 'key': UAKey, }

CToUAMethod = ['put', 'get', ]
CToUAhead = ['Action', ]
CToUAKey = ['Run', 'Terminate', 'Restart', 'System', ]
CToUADict = {'method': CToUAMethod, 'head': CToUAhead, 'key': CToUAKey, 'data': None, }


