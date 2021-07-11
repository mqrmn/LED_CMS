import win32pdh

class API:
    def GetProcessList(self):
        junk, list = win32pdh.EnumObjectItems(None, None, "Процесс", win32pdh.PERF_DETAIL_WIZARD)
        return list

    def CheckProcess(self, name):
        if name in self.GetProcessList():
            state = True
        else:
            state = False
        return state

    def CheckProcessNovaStudio(self):
        name = 'NovaStudio'
        return self.CheckProcess(name)

    def CheckProcessMarsServer(self):
        pass
    def CheckProcessYaDisk(self):
        pass