# 1.1.1
import sys
from peewee import *

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config
from App import Resource as Res

db_handle = SqliteDatabase(Config.DBPath)


class BaseModel(Model):
    id = AutoField()

    class Meta:
        database = db_handle


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

    def create_tables(self):
        with db_handle:
            db_handle.create_tables([self.SelfInitShutdown, ])
            db_handle.create_tables([self.SystemRun, ])
            db_handle.create_tables([self.SystemInit, ])

    def get_count(self):

        count = self.SystemRun().select().count()
        return count

    def write_controller(self, q_in):
        while True:
            data = q_in.get()
            if data['table'] == 'SystemInit':
                wr_data = data['data']
                self.SystemInit.create(id=wr_data['id'], datetime=wr_data['datetime'], )

            if data['table'] == 'SystemRun':
                wr_data = data['data']
                self.SystemRun.create(datetime=wr_data['datetime'], )

            if data['table'] == 'SelfInitShutdown':
                wr_data = data['data']
                self.SelfInitShutdown.create(id=wr_data['id'], trigger=wr_data['trigger'],
                                             key=wr_data['key'], datetime=wr_data['datetime'], )

    def read_controller(self):
        pass


class Prepare(DBFoo):

    def self_init_shutdown_prep(self, trigger, key, datetime_data):
        return {Res.r[1]: Res.H[3],
                Res.r[2]: Res.K[8],
                Res.r[3]: {Res.DBWriteData[0]: 'SelfInitShutdown',
                           Res.r[3]: {'id': self.get_count(),
                                      'trigger': trigger,
                                      'key': key,
                                      'datetime': datetime_data},
                           }, }

    def system_init_prep(self, datetime_data):
        return {Res.r[1]: Res.H[3],
                Res.r[2]: Res.K[8],
                Res.r[3]: {Res.DBWriteData[0]: 'SystemInit',
                           Res.r[3]: {'id': self.get_count(),
                                      'datetime': datetime_data,
                                      }, }, }

    @staticmethod
    def system_run_prep(datetime_data):
        return {Res.r[1]: Res.H[3],
                Res.r[2]: Res.K[8],
                Res.r[3]: {Res.DBWriteData[0]: 'SystemRun',
                           Res.r[3]: {'datetime': datetime_data,
                                      }, }, }
