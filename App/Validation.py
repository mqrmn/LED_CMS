# 1.1.1

import sys


sys.path.append("C:\\MOBILE\\Local\\CMS")


from App import LogManager

LOG = LogManager.Log_Manager()

class System:

    def Threads(self, Threads):
        state = []
        for i in Threads:
            state.append(i.is_alive())
        return state

