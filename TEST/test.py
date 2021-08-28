

from App import Database
import datetime


def TEST():
    handle = Database.Prepare()
    print(type(handle.GetCount()))

    print(handle.SystemInitPrep(datetime.datetime.now()))




if __name__ == '__main__':
    TEST()