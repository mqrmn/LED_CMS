# 1.1.1

# ROOT
root = ['method', 'head', 'key', 'data']
Method = ['put', 'get', ]
Head = ['State', 'Action', 'Report', 'DB', 'Flag']
Key = ['ScreenState', 'ProcState', 'RunProc', 'TerminateProc', 'RestartProc',
       'Process', 'TerminateThread', 'UALastAction', 'DBWrite', 'UAValid',
       'CMSController', ]

DBWriteData = ['table', ]
ShutdownFlagData = [0, 1, 2, ]





# PROCESS
ProcList = ['NovaStudio.exe', 'MarsServerProvider.exe', 'NovaSoftwareDog.exe', 'NovaLCT.exe', ]
ProcState = [True, False]

# SCREEN
ScreenKey = ['ScreenIsStatic', ]
ScreenState = ['Static', ]

# ACTION
ActionKey = ['RunNova', 'RestartNova', 'TerminateNova', 'RestartSystem', ]

### NOT IN USE

NovaFileKey = {'Backup', 'Restore', }
stateKey = [['ScreenState', ['ScreenIsStatic', ], ], ['ProcessState', ['NovaStudio.exe', 'MarsServerProvider.exe', ], ], ]
System = ['Reboot', 'Shutdown', ]

# SUMMARY
ComDict = {root[0]: Method,
             root[1]: Head,
             root[2]: Key,
             root[3]: {Key[0]: ScreenState,
                      Key[1]: ProcState,
                      Key[2]: ProcList,
                      Key[3]: ProcList,
                      Key[4]: ProcList,
                      Key[5]: System, }, }


### DEPENDENCY

# PROC STATE
ProcDict = {ProcList[0]: True, ProcList[1]: False, }

# ACTIONS WITH DEPENDENCY
RunNova = [{Key[1]: [ProcList[0], False], Key[0]: [ScreenState[0], True]},
                {root[1]: Head[1], root[2]: Key[2], root[3]: ProcList[0], }, ]

RestartNova = [{Key[1]: [ProcList[0], True], Key[0]: [ScreenState[0], True]},
                {root[1]: Head[1], root[2]: Key[4], root[3]: ProcList[0], }, ]

TerminateMars = [{Key[1]: [ProcList[1], False], },
                 {root[1]: Head[1], root[2]: Key[3], root[3]: ProcList[1], }, ]

TerminateNova = [{root[1]: Head[1], root[2]: Key[3], root[3]: ProcList[0], }, ]

TerminateNovaSD = [{root[1]: Head[1], root[2]: Key[3], root[3]: ProcList[2], }, ]

TerminateThread = [{root[0]:Method[0], root[1]: Head[1],  root[2]: Key[6], root[3]: 'UA_All', }, ]

# Зарезервированные словари команд
Res_ContinueNova = {Key[1]: [ProcList[0], True], Key[0]: [ScreenState[0], False]}
Res_Reserved = {Key[1]: [ProcList[0], False], Key[0]: [ScreenState[0], False]}
Res_ContinueMars = {Key[1]: [ProcList[1], True], }

CMSCore = 'CMSCore'