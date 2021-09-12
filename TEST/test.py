

from App import Database
import datetime


def TEST():
    handle = Database.Prepare()
    print(type(handle.GetCount()))
    print(handle.SystemInitPrep(datetime.datetime.now()))
    print(type(handle.SystemInitPrep(datetime.datetime.now())['data']['data']['id']))

    data = handle.SystemInitPrep(datetime.datetime.now())['data']['data']
    print(data)
    handle.SystemInit.create(id=data['id'], datetime=data['datetime'], )



if __name__ == '__main__':
    TEST()