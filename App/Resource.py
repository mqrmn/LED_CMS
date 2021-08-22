# 1.1.1

# ROOT
root = ['method', 'head', 'key', 'data']
Method = ['put', 'get', ]
Head = ['State', 'Action', 'Report', 'DB', 'Flag']
Key = ['ScreenState', 'ProcState', 'RunProc', 'TerminateProc', 'RestartProc',
       'Process', 'TerminateThread', 'UALastAction', 'DBWrite', 'UAValid',
       'CMSController', ]

# DB
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