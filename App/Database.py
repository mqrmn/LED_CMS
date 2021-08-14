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
    class Meta:
        database = database

class Tables(BaseModel):

    class SelfInitShutdown(BaseModel):
        id = AutoField()
        trigger = TextField()
        datetime = DateTimeField()

class DBFoo(Tables):

    def CreateTables(self):
        with database:
            database.create_tables([self.SelfInitShutdown, ])


    def WriteController(self, Q_in):
        while True:
            data = Q_in.get()
            print(data)

    def ReadController(self):
        pass
