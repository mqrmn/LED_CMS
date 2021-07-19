


NovaFileKey = {'Backup', 'Restore', }
ActionKey = ['RunNova', 'RestartNova', 'TerminateNova', 'RestartSystem', ]
ScreenKey = ['ScreenIsStatic', ]
stateKey = [['ScreenState', ['ScreenIsStatic', ], ], ['ProcessState', ['NovaStudio', 'MarsServerProvider', ], ], ]



# Содержание словаря обмена
Method = ['put', 'get', ]
Head = ['State', 'Action', ]
Key = ['ScreenState', 'ProcState', 'RunProc', 'TerminateProc', 'RestartProc', 'System', ]
ProcState = [True, False]
ProcList = ['NovaStudio', 'MarsServerProvider', ]
ScreenState = ['Static', ]
System = ['Reboot', 'Shutdown', ]

# Шаблон словаря обмена
ComDict = {'method': Method,
             'head': Head,
             'key': Key,
             'data': {'ScreenState': ScreenState,
                      'ProcState': ProcState,
                      'RunProc': ProcList,
                      'TerminateProc': ProcList,
                      'RestartProc': ProcList,
                      'System': System, }, }

# Настройки состояния процессов
ProcDict = {ProcList[0]: True, ProcList[1]: False, }

# Словари команд
RunNova = [{'ProcState': ['NovaStudio', False], 'ScreenState': ['Static', True]},
           {'head': 'Action', 'key': 'RunProc', 'data': 'NovaStudio', }, ]
RestartNova = [{'ProcState': ['NovaStudio', True], 'ScreenState': ['Static', True]},
               {'head': 'Action', 'key': 'RestartProc', 'data': 'NovaStudio', }, ]
TerminateMars = [{'ProcState': ['MarsServerProvider', False], },
                 {'ProcState': ['MarsServerProvider', False], }, ]

# Зарезервированные словари команд
Res_ContinueNova = {'ProcState': ['NovaStudio', True], 'ScreenState': ['Static', False]}
Res_Reserved = {'ProcState': ['NovaStudio', False], 'ScreenState': ['Static', False]}
Res_ContinueMars = {'ProcState': ['MarsServerProvider', True], }