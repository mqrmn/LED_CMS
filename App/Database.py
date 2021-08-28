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
        id = IntegerField()
        trigger = TextField()
        key = TextField()
        datetime = DateTimeField()
        class Meta:
            db_table = "SelfInitShutdown"
            order_by = ('-id',)

    class SystemInit(BaseModel):
        id = IntegerField()
        datetime = DateTimeField()
        class Meta:
            db_table = "SystemInit"
            order_by = ('-id',)

    class SystemRun(BaseModel):
        datetime = DateTimeField()
        class Meta:
            db_table = "SystemRun"
            order_by = ('-id',)



class DBFoo(Tables):

    def CreateTables(self):
        with dbhandle:
            dbhandle.create_tables([self.SelfInitShutdown, ])
            dbhandle.create_tables([self.SystemRun, ])
            dbhandle.create_tables([self.SystemInit, ])
    def GetCount(self):

        count = self.SystemRun().select().count()
        return count

    def WriteController(self, Q_in):
        while True:
            data = Q_in.get()
            if data['table'] == 'SystemInit':
                wrData = data['data']
                self.SystemInit.create(id=wrData['id'], datetime=wrData['datetime'], )

            if data['table'] == 'SystemRun':
                wrData = data['data']
                self.SystemRun.create(datetime=wrData['datetime'], )

            if data['table'] == 'SelfInitShutdown':
                wrData = data['data']
                self.SelfInitShutdown.create(id=wrData['id'], trigger=wrData['trigger'], key=wrData['key'], datetime=wrData['datetime'], )

    def ReadController(self):
        pass


class Prepare(DBFoo):

    def SelfInitShutdownPrep(self, trigger, key, datetimeData):
        return {R.r[1]: R.H[3],
                R.r[2]: R.K[8],
                R.r[3]: {R.DBWriteData[0]: 'SelfInitShutdown',
                                R.r[3]: {'id': self.GetCount(),
                                            'trigger': trigger,
                                            'key': key,
                                            'datetime': datetimeData},
                                                }, }

    def SystemInitPrep(self, datetimeData):
        return {R.r[1]: R.H[3],
                R.r[2]: R.K[8],
                R.r[3]: {R.DBWriteData[0]: 'SystemInit',
                                R.r[3]: {'id':self.GetCount(),
                                            'datetime': datetimeData,
                                                }, }, }

    def SystemRunPrep(self, datetimeData):
        return {R.r[1]: R.H[3],
                R.r[2]: R.K[8],
                R.r[3]: {R.DBWriteData[0]: 'SystemRun',
                                R.r[3]: {'datetime': datetimeData,
                                                }, }, }