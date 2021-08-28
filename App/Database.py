# 1.1.1
import sys
from peewee import *

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config
from App import Resource as R

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
                data = data['data']
                self.SystemInit.create(datetime=data['datetime'], )

            if data['table'] == 'SystemRun':
                data = data['data']
                self.SystemRun.create(datetime=data['datetime'], )

            if data['table'] == 'SelfInitShutdown':
                data = data['data']
                self.SelfInitShutdown.create(trigger=data['trigger'], key=data['key'], datetime=data['datetime'], )

    def ReadController(self):
        pass


class Prepare:

    def SelfInitShutdown(self, trigger, key, datetimeData):
        return {R.r[1]: R.H[3],
                R.r[2]: R.K[8],
                R.r[3]: {R.DBWriteData[0]: 'SelfInitShutdown',
                                R.r[3]: {'trigger': trigger,
                                                      'key': key,
                                                      'datetime': datetimeData}, }, }

    def SystemInit(self, datetimeData):
        return {R.r[1]: R.H[3],
                R.r[2]: R.K[8],
                R.r[3]: {R.DBWriteData[0]: 'SystemInit',
                                R.r[3]: {'datetime': datetimeData,
                                                }, }, }

    def SystemRun(self, datetimeData):
        return {R.r[1]: R.H[3],
                R.r[2]: R.K[8],
                R.r[3]: {R.DBWriteData[0]: 'SystemRun',
                                R.r[3]: {'datetime': datetimeData,
                                                }, }, }