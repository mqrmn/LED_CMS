# 1.1.1

import sys

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import Log

LOG = Log.LogManager()


class System:

    @staticmethod
    def threads(threads):
        state = []
        for i in threads:
            state.append(i.is_alive())
        return state
