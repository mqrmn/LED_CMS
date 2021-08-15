# 1.1.1
import sys
import os
from inspect import currentframe, getframeinfo
from peewee import *
from App.Config import Config

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config
from App import Resource, LogManager

logging = LogManager._Log_Manager_()
logHandler = logging.InitModule(os.path.splitext(os.path.basename(__file__))[0])

database = SqliteDatabase(Config.DBPath)

class BaseModel(Model):
    id = AutoField()
    class Meta:
        database = database

class Tables(BaseModel):

    class SelfInitShutdown(BaseModel):
        id = AutoField()
        trigger = TextField()
        datetime = DateTimeField()

    class SystemRun(BaseModel):
        datetime = DateTimeField()

    class SystemInit(BaseModel):
        datetime = DateTimeField()

class DBFoo(Tables):

    def CreateTables(self):
        with database:
            database.create_tables([self.SelfInitShutdown, ])


    def WriteController(self, Q_in):
        while True:
            data = Q_in.get()
            print('WriteController', data)
            if data['table'] == 'SystemInit':
                print('WriteController', 'SystemInit', data)
            if data['table'] == 'SelfInitShutdown':
                data = data['data']
                self.SelfInitShutdown.create(trigger=data['trigger'], datetime=data['datetime'], )

                print('WriteController', 'SelfInitShutdown', data)

    def ReadController(self):
        pass
class Prepare:

    def SelfInitShutdown(self, trigger, datetimeData):
        return {Resource.root[1]: Resource.Head[3],
                Resource.root[2]: Resource.Key[8],
                Resource.root[3]: {Resource.Data[0]: 'SelfInitShutdown',
                                   Resource.root[3]: {'trigger': trigger,
                                                      'datetime': datetimeData}, }, }