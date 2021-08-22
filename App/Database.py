# 1.1.1
import sys
import os
from inspect import currentframe, getframeinfo

from peewee import *
from App.Config import Config

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config
from App import Resource, Log

logging = Log.Log_Manager()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])

dbhandle = SqliteDatabase(Config.DBPath)



class BaseModel(Model):
    id = AutoField()
    class Meta:
        database = dbhandle

class Tables:

    class SelfInitShutdown(BaseModel):
        trigger = TextField()
        key = TextField()
        datetime = DateTimeField()
        class Meta:
            db_table = "SelfInitShutdown"
            order_by = ('-id',)

    class SystemRun(BaseModel):
        datetime = DateTimeField()

    class SystemInit(BaseModel):
        datetime = DateTimeField()

class DBFoo(Tables):

    def CreateTables(self):
        with dbhandle:
            dbhandle.create_tables([self.SelfInitShutdown, ])
            dbhandle.create_tables([self.SystemRun, ])
            dbhandle.create_tables([self.SystemInit, ])

    def WriteController(self, Q_in):
        while True:
            data = Q_in.get()
            if data['table'] == 'SystemInit':
                print('WriteController', 'SystemInit', data)
            if data['table'] == 'SelfInitShutdown':
                data = data['data']
                self.SelfInitShutdown.create(trigger=data['trigger'], key=data['key'], datetime=data['datetime'], )
                print('SelfInitShutdown', data)

    def ReadController(self):
        pass


class Prepare:

    def SelfInitShutdown(self, trigger, key, datetimeData):
        return {Resource.r[1]: Resource.H[3],
                Resource.r[2]: Resource.K[8],
                Resource.r[3]: {Resource.DBWriteData[0]: 'SelfInitShutdown',
                                Resource.r[3]: {'trigger': trigger,
                                                      'key': key,
                                                      'datetime': datetimeData}, }, }

    def SystemInit(self, datetimeData):
        return {Resource.r[1]: Resource.H[3],
                Resource.r[2]: Resource.K[8],
                Resource.r[3]: {Resource.DBWriteData[0]: 'SystemInit',
                                Resource.r[3]: {'datetime': datetimeData,
                                                }, }, }