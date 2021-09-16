# 1.1.1

# ROOT
# root
r = ['method', 'head', 'key', 'data']
# Method
M = ['put', 'get', ]
# Head
H = ['State', 'Action', 'Report', 'DB', 'Flag', 'Mail']
# Key
K = ['ScreenState', 'ProcState', 'RunProc', 'TerminateProc', 'RestartProc',  # 0 - 4
     'Process', 'TerminateThread', 'UALastAction', 'DBWrite', 'UAValid',  # 5 - 9
     'CMSController', 'RestoreNovaBin', 'SendMail', 'System']             # 10 - 13

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
ActionKey = ['RunNova', 'RestartNova', 'TerminateNova', 'RestartSystem', 'RestoreNovaBin', ]

# DEPENDENCY

# PROC STATE
ProcDict = {ProcList[0]: True, ProcList[1]: False, }


# ACTIONS WITH DEPENDENCY
RunNova = [{K[1]: [ProcList[0], False], K[0]: [ScreenState[0], True]},
           {r[1]: H[1], r[2]: K[2], r[3]: ProcList[0], }, ]

RestartNova = [{K[1]: [ProcList[0], True], K[0]: [ScreenState[0], True]},
               {r[1]: H[1], r[2]: K[4], r[3]: ProcList[0], }, ]

TerminateMars = [{K[1]: [ProcList[1], False], },
                 {r[1]: H[1], r[2]: K[3], r[3]: ProcList[1], }, ]

TerminateNova = [{r[1]: H[1], r[2]: K[3], r[3]: ProcList[0], }, ]

TerminateNovaSD = [{r[1]: H[1], r[2]: K[3], r[3]: ProcList[2], }, ]

TerminateThread = [{r[0]:M[0], r[1]: H[1], r[2]: K[6], r[3]: 'UA_All', }, ]

RestoreNovaBin = [{r[1]: H[1], r[2]: K[11], r[3]: True}]


class CreateMessage:

    @staticmethod
    def send_mail(msg_txt):
        return {r[1]: H[5], r[2]: K[12], r[3]: msg_txt, }

    @staticmethod
    def set_flag_uav_0():
        return {r[1]: H[4], r[2]: K[9], r[3]: ShutdownFlagData[0]}

    @staticmethod
    def set_flag_cont_0():
        return {r[1]: H[4], r[2]: K[10], r[3]: ShutdownFlagData[0]}

    @staticmethod
    def set_flag_uav_1():
        return {r[1]: H[4], r[2]: K[9], r[3]: ShutdownFlagData[1]}

    @staticmethod
    def set_flag_cont_1():
        return {r[1]: H[4], r[2]: K[10], r[3]: ShutdownFlagData[1]}

    @staticmethod
    def set_flag_uav_2():
        return {r[1]: H[4], r[2]: K[9], r[3]: ShutdownFlagData[2]}

    @staticmethod
    def set_flag_cont_2():
        return {r[1]: H[4], r[2]: K[10], r[3]: ShutdownFlagData[2]}

    @staticmethod
    def reboot_system():
        return {r[1]: H[1], r[2]: K[13], r[3]: ActionKey[3]}

    @staticmethod
    def command_run_nova():
        return {r[1]: H[1], r[2]: K[2], r[3]: ProcList[0], }

    @staticmethod
    def command_term_nova():
        return {r[1]: H[1], r[2]: K[3], r[3]: ProcList[0], }