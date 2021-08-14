
import datetime
from App import Action
from App.Database import *

def TEST():

    #
    # handle = DBFoo()
    # handle.CreateTables()

    # SelfInitShutdown.create(trigger='TextField', datetime=datetime.datetime.now(), )

    C_Action = Action.Init()
    C_Action.CMS()



if __name__ == '__main__':
    TEST()