

from App import Database
import datetime


def TEST():
    handle = Database.Prepare()
    print(type(handle.get_count()))
    print(handle.system_init_prep(datetime.datetime.now()))
    print(type(handle.system_init_prep(datetime.datetime.now())['data']['data']['id']))

    data = handle.system_init_prep(datetime.datetime.now())['data']['data']
    print(data)
    handle.SystemInit.create(id=data['id'], datetime=data['datetime'], )



if __name__ == '__main__':
    TEST()