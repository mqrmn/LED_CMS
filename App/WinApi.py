import win32pdh
from App import Resource

class _API_:
    def GetProcessList(self):
        junk, list = win32pdh.EnumObjectItems(None, None, "Процесс", win32pdh.PERF_DETAIL_WIZARD)
        return list

    def GetProcessState(self, Q_out):
        processList = self.GetProcessList()
        for i in Resource.ProcessList:
            if i in processList:
                procState = True
            else:
                procState = False
            Q_out.put([i, procState])