# 1.1.1

import sys
import time
import os
import shutil
import re
import datetime
import win32evtlog
import win32evtlogutil
import win32con
import winerror
from datetime import date

sys.path.append("C:\\MOBILE\\Local\\CMS")
from App.Config import Config
from App import API, Log, Database, File
from App import Resource as Res

LOG = Log.LogManager()

global o_nova
global o_sys
global o_file


class Init:
    def __init__(self):
        global o_nova
        global o_sys
        global o_file
        o_nova = API.Nova()
        o_sys = API.System()
        o_file = File.NovaBin()


class Process(Init):

    @staticmethod
    def start(data):
        if data == Res.ProcList[0]:
            o_nova.run_nova()

    @staticmethod
    def terminate(data):
        if data == Res.ProcList[1]:
            o_nova.terminate_mars()
        if data == Res.ProcList[0]:
            o_nova.terminate_nova()

    @staticmethod
    def restart(data):
        if data == Res.ProcList[0]:
            o_nova.restart_nova()


class System(Init):

    @staticmethod
    def pre_shutdown():
        o_file.backup_handle()

    def reboot_init(self):
        self.pre_shutdown()
        time.sleep(30)
        o_sys.restart_pc()


class Files(Init):

    # Archives logs
    @staticmethod
    def log_arch():
        arch_name = None
        # arch_name = None
        list_for_archiving = []
        # Lists files stored in a directory
        for file in os.listdir(Config.logPath):
            # Continues to work only with files with the .log extension
            if re.search('log', file):
                # Checks the creation date of log files
                log_date = datetime.datetime.strptime(re.findall(r'\d{4}-\d{2}-\d{2}', file)[0], "%Y-%m-%d")
                if log_date.date() < date.today():
                    arch_name = str(log_date.date())
                    LOG.cms_logger('Marked for archiving ' + file)
                    list_for_archiving.append(file)
        # Checks if the folder that I'm going to create exists
        if list_for_archiving and not os.path.exists(Config.logPath + str(date.today())):
            os.mkdir(Config.logPath + arch_name)
            # Move logs to folder
            for file in list_for_archiving:
                shutil.move(Config.logPath + file, Config.logPath + arch_name + '\\' + file)
                LOG.cms_logger('Moved to archive ' + file)
            # Archives a folder
            shutil.make_archive(base_name=Config.logPath + arch_name,
                                format='zip', root_dir=Config.logPath + arch_name, )
            shutil.rmtree(Config.logPath + arch_name)
        else:
            LOG.cms_logger('No logs found to archive')

    # Removes obsolete logs
    @staticmethod
    def log_del():
        list_for_deleting = []

        # Lists files stored in a directory
        for file in os.listdir(Config.logPath):
            # Continues to work only with files with the .zip extension
            if re.search('zip', file):
                # Checks the date the archive was created
                if (datetime.datetime.strptime(re.findall(r'\d{4}-\d{2}-\d{2}', file)[0],
                                               "%Y-%m-%d").date() - date.today()).days < -90:
                    list_for_deleting.append(file)

        # Removes obsolete archives
        for file in list_for_deleting:
            os.remove(Config.logPath + file)
            LOG.cms_logger('File deleted ' + file)


class SysInit(Files):
    def init_cms(self, q_internal):
        data = self.check_self()
        self.put_sys_run(q_internal)
        self.log_arch()
        self.log_del()

        self.check_last_self_init_std(q_internal)
        if data is True:
            self.check_last_std(q_internal)
        else:
            pass

    @staticmethod
    def check_db():
        data = True
        if os.path.exists(Config.DBFolder):
            if os.path.exists(Config.DBPath):
                LOG.cms_logger('Database file exist')
            else:
                handle = Database.DBFoo()
                handle.create_tables()
                data = False
                LOG.cms_logger('Database file created')
        else:
            os.mkdir(Config.DBFolder)
            handle = Database.DBFoo()
            handle.create_tables()
            data = False
            LOG.cms_logger('Database file created')
        return data

    def check_self(self):
        data = self.check_db()
        return data

    @staticmethod
    def put_sys_run(q_out):
        o_db_prep = Database.Prepare()
        q_out.put(o_db_prep.system_run_prep(datetime.datetime.now()))

    @staticmethod
    def check_last_self_init_std(q_internal):
        table = Database.Tables()
        cr_msg = Res.CreateMessage()

        try:
            last_std = table.SelfInitShutdown().select().order_by(table.SelfInitShutdown.id.desc()).get()
        except:
            last_std = None
        if last_std:
            count = table.SelfInitShutdown().select().where(
                (table.SelfInitShutdown.datetime.year == datetime.date.today().year) &
                (table.SelfInitShutdown.datetime.month == datetime.date.today().month) &
                (table.SelfInitShutdown.datetime.day == datetime.date.today().day)).count()
            if last_std.datetime.date() == datetime.datetime.now().date():
                if (datetime.datetime.now() - last_std.datetime).seconds <= 600:
                    if count >= 2:
                        q_internal.put(cr_msg.set_flag_uav_0())
                        q_internal.put(cr_msg.set_flag_cont_0())

                        msg = 'Exceeded quantity Attempts to restart the system: ' \
                              '{} Last reboot: {} '.format(count, last_std.datetime)

                        q_internal.put(cr_msg.send_mail(msg))
                        LOG.cms_logger(msg)
                        LOG.cms_logger('Restart prohibited ')
                    else:
                        q_internal.put(cr_msg.set_flag_uav_1())
                        q_internal.put(cr_msg.set_flag_cont_1())

                        msg = 'The frequency of attempts to restart the system has ' \
                              'been exceeded Last reboot: {} '.format(last_std.datetime)

                        LOG.cms_logger(msg)
                elif count >= 5:
                    q_internal.put(cr_msg.set_flag_uav_1())
                    q_internal.put(cr_msg.set_flag_cont_1())

                    msg = 'The frequency of attempts to ' \
                          'restart the system has been exceeded ' \
                          'Last reboot: {} '.format(last_std.datetime)

                    q_internal.put(cr_msg.send_mail(msg))
                    LOG.cms_logger(msg)

                    LOG.cms_logger('Restart prohibited')
                else:
                    q_internal.put(cr_msg.set_flag_uav_2())
                    q_internal.put(cr_msg.set_flag_cont_2())

                    LOG.cms_logger('Restart allowed')
            else:
                q_internal.put(cr_msg.set_flag_uav_2())
                q_internal.put(cr_msg.set_flag_cont_2())

                LOG.cms_logger('Restart allowed')
        else:
            q_internal.put(cr_msg.set_flag_uav_2())
            q_internal.put(cr_msg.set_flag_cont_2())

            LOG.cms_logger('No data on system reboots')
            LOG.cms_logger('Restart allowed')

    @staticmethod
    def check_last_std(q_internal):
        o_cr_msg = Res.CreateMessage()
        o_tbl = Database.Tables()

        machine = None
        ev = True
        br = False
        pre_current_run = None
        last_std = None
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        ev_types = {win32con.EVENTLOG_INFORMATION_TYPE: 'EVENTLOG_INFORMATION_TYPE',
                    win32con.EVENTLOG_WARNING_TYPE: 'EVENTLOG_WARNING_TYPE',
                    win32con.EVENTLOG_ERROR_TYPE: 'EVENTLOG_ERROR_TYPE'}
        log_type = 'System'
        handle = win32evtlog.OpenEventLog(machine, log_type)
        ev_source = ['User32', 'Microsoft-Windows-Winlogon',
                     'Microsoft-Windows-Kernel-Power',
                     'Microsoft-Windows-Kernel-Boot',
                     'EventLog', 'Kernel-Boot']

        time.sleep(10)
        current_run = o_tbl.SystemRun().select().order_by(o_tbl.SystemRun.id.desc()).get()
        if o_tbl.SystemRun().select().count() == 1:
            LOG.cms_logger('CMS запущена впервые на этекущей системе')
            exit()
        else:
            pre_current_run = o_tbl.SystemRun().select().where(o_tbl.SystemRun.id == current_run.id - 1).get()

        if o_tbl.SelfInitShutdown().select().count() == 0:
            LOG.cms_logger('CMS еще не отключал текущую систему')
            exit()
        else:
            last_std = o_tbl.SelfInitShutdown().select().where(
                o_tbl.SelfInitShutdown.key == ('reboot' or 'shutdown')).order_by(o_tbl.SelfInitShutdown.id.desc()).get()

        time_line = (datetime.datetime.now() - pre_current_run.datetime).seconds

        if last_std.id != pre_current_run.id:
            msg_txt = 'Предыдущее отключение не было инициировано CMS, либо произошел сбой записи в БД \n'
            while ev:
                try:
                    ev = win32evtlog.ReadEventLog(handle, flags, 0)
                    for ev_obj in ev:
                        the_time = ev_obj.TimeGenerated

                        if (datetime.datetime.now() - the_time).seconds <= time_line:
                            if str(ev_obj.SourceName) in ev_source:
                                src = str(ev_obj.SourceName)
                                ev_type = str(ev_types[ev_obj.EventType])
                                msg = str(win32evtlogutil.SafeFormatMessage(ev_obj, log_type))
                                ev_id = str(winerror.HRESULT_CODE(ev_obj.EventID))

                                if src == 'User32' and ev_id == '1074':
                                    if re.findall(r'RuntimeBroker.exe', msg):
                                        if re.findall(r'Перезапустить', msg):
                                            msg_txt += 'Система была перезагружена пользователем, \n' \
                                                       'Время: {}, \n' \
                                                       'Тип: {}, \n' \
                                                       'Источник: {}, \n' \
                                                       'Код события: {}, \n' \
                                                       'Описание: {} '.format(the_time.Format(),
                                                                              ev_type, src, ev_id, msg)
                                            br = True

                                        elif re.findall(r'Выключение питания', msg):
                                            msg_txt += 'Система была выключена пользователем, ' \
                                                       'Время: {}, \n' \
                                                       'Тип: {}, \n' \
                                                       'Источник: {}, \n' \
                                                       'Код события: {}, \n' \
                                                       'Описание: {} '.format(the_time.Format(), ev_type, src, ev_id,
                                                                              msg)
                                            br = True
                        if br is True:
                            break
                    if br is True:
                        break
                except 'Exception':
                    pass
            if msg_txt:
                LOG.cms_logger(msg_txt)
                q_internal.put(o_cr_msg.send_mail(msg_txt))
            win32evtlog.CloseEventLog(handle)
