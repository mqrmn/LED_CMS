# 1.1.1

import sys
import time
import datetime

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import File, Act, Database, Log, Notify
from App import Resource as Res
from App.Config import Config as Conf

LOG = Log.LogManager()

global o_CrMsg
global o_Act
global o_DBMsg
global o_crMailMsg


class Init:
    def __init__(self):
        global o_CrMsg
        global o_Act
        global o_DBMsg
        global o_crMailMsg

        o_DBMsg = Database.Prepare()
        o_CrMsg = Res.CreateMessage()
        o_Act = Act.System()
        o_crMailMsg = Notify.Mail()


# Queue handlers
class Queue(Init):
    def send_controller(self, q_prepare_to_send, q_tcp_send, q_internal=None, ):

        null_datetime = datetime.datetime.strptime('2020-02-02', "%Y-%m-%d")

        term_nova_time = null_datetime
        term_mars_time = null_datetime
        res_nova_time = null_datetime
        run_nova_time = null_datetime

        while True:
            data = q_prepare_to_send.get()

            # Launching NovaStudio
            if data == Res.RunNova[1]:
                if (datetime.datetime.now() - run_nova_time).seconds >= Conf.runNovaTimeout:
                    self.to_send(data, q_tcp_send)
                    run_nova_time = datetime.datetime.now()
                else:
                    pass
                data = None
            # Stop NovaStudio
            if data == Res.TerminateNova:
                if (datetime.datetime.now() - term_nova_time).seconds >= Conf.terminateNovaTimeout:
                    self.to_send(data, q_tcp_send)
                    term_nova_time = datetime.datetime.now()
                else:
                    pass
                data = None
            # Stopping MarsServerProvider
            if data == Res.TerminateMars[1]:
                if (datetime.datetime.now() - term_mars_time).seconds >= Conf.terminateMarsTimeout:
                    self.to_send(data, q_tcp_send)
                    term_mars_time = datetime.datetime.now()
                else:
                    pass
                data = None
            # Restarting NovaStudio
            if data == Res.RestartNova[1]:
                if (datetime.datetime.now() - res_nova_time).seconds >= Conf.restartNovaTimeout:
                    self.to_send(data, q_tcp_send)
                    res_nova_time = datetime.datetime.now()
                else:
                    pass
                data = None

            if data is not None:
                self.to_send(data, q_tcp_send)

    # Handler for the queue of data coming from CMSUserAgent
    @staticmethod
    def from_ua(q_from_ua, q_valid_screen, q_valid_proc, q_internal):
        while True:
            data = q_from_ua.get()
            last_receive = datetime.datetime.now()
            if data[Res.r[0]] == Res.M[0]:
                if data[Res.r[1]] == Res.H[0]:
                    if data[Res.r[2]] == Res.K[0]:
                        q_valid_screen.put({Res.r[2]: data[Res.r[2]], Res.r[3]: data[Res.r[3]], })
                    if data[Res.r[2]] == Res.K[1]:
                        q_valid_proc.put({Res.r[2]: data[Res.r[2]], Res.r[3]: data[Res.r[3]], })

            q_internal.put({Res.r[1]: Res.H[2],
                            Res.r[2]: Res.K[7],
                            Res.r[3]: last_receive, })

    # Prepares commands to be sent to the UA
    @staticmethod
    def create_action(q_action, q_prepare_to_send, q_internal):
        restart_nova_count = 0
        restore_nova_count = 0
        last_nova_restart = None
        dict_nova = {}
        dict_mars = {}
        command = None

        while True:

            data = q_action.get()
            if (data[Res.r[2]] == Res.K[0]) \
                    or (data[Res.r[2]] == Res.K[1]
                        and data[Res.r[3]][0] == Res.ProcList[0]):
                dict_nova[data[Res.r[2]]] = data[Res.r[3]]

                # Run Nova
                if dict_nova == Res.RunNova[0]:
                    command = Res.RunNova[1]
                    dict_nova = {}
                # Restart Nova
                if dict_nova == Res.RestartNova[0]:
                    command = Res.RestartNova[1]
                    dict_nova = {}
                    restart_nova_count += 1
                    last_nova_restart = datetime.datetime.now()
                if command:
                    q_prepare_to_send.put(command)
                    command = None
                    dict_nova = {}

            if data[Res.r[2]] == Res.K[1] \
                    and data[Res.r[3]][0] == Res.ProcList[1]:
                dict_mars[data[Res.r[2]]] = data[Res.r[3]]
                # TerminateMars
                if dict_mars == Res.TerminateMars[0]:
                    command = Res.TerminateMars[1]
                    dict_mars = {}
                if command:
                    q_prepare_to_send.put(command)
                    command = None
                    dict_mars = {}
            # RestoreNova
            if restart_nova_count >= Conf.restartNovaMaxCount \
                    and ((datetime.datetime.now() - last_nova_restart).seconds <= Conf.restartNovaTimeout):
                q_prepare_to_send.put(Res.RestoreNovaBin[0])
                restore_nova_count += 1
                restart_nova_count = 0
                if restore_nova_count >= Conf.restoreNovaMaxCount:
                    a = o_CrMsg.reboot_system()
                    b = o_CrMsg.send_mail('The system attempt to reboot')
                    q_internal.put(a)
                    q_internal.put(b)

    # Processor of data coming to UA
    @staticmethod
    def from_core(q_in, q_out, ):
        while True:
            data = q_in.get()
            if data[Res.r[0]] == Res.M[0]:      # Method == put
                if data[Res.r[1]] == Res.H[1]:  # Head == Action
                    q_out.put(data)
                if data[Res.r[1]] == Res.H[4]:  # Head == Flag
                    q_out.put(data[Res.r[3]])

    @staticmethod
    def from_core_to_cont(q_in, q_out, ):
        data = q_in.get()
        if data[Res.r[0]] == Res.M[0]:  # Method == put
            if data[Res.r[1]] == Res.H[4]:  # Head == Flag
                q_out.put(data)

    # Checks the keys in the data coming to the UA, in accordance with them, launches actions
    @staticmethod
    def ua_action(q_in, q_out, ):
        c_exec = Act.Process()
        c_file = File.NovaBin()
        while True:
            data = q_in.get()
            if data[Res.r[2]] == Res.K[2]:      # Key == RunProc
                c_exec.start(data[Res.r[3]])
            if data[Res.r[2]] == Res.K[3]:      # Key == TerminateProc
                c_exec.terminate(data[Res.r[3]])
            if data[Res.r[2]] == Res.K[4]:      # Key == RestartProc
                c_exec.restart(data[Res.r[3]])
            if data[Res.r[2]] == Res.K[5]:      # Key == Process
                pass
            if data[Res.r[2]] == Res.K[6]:      # Key == TerminateThread
                q_out.put(data)
            if data[Res.r[2]] == Res.K[11]:     # Key == RestoreNovaBin
                c_file.restore_handle()

    # Checks the flow of incoming data for a given match
    @staticmethod
    def valid(q_in, q_out, check_value, max_count, head, send_all_circles, ):
        check_count, catch_count = 0, 0
        dict_d = {}

        while True:
            data = q_in.get()
            if type(data) == dict_d:
                if data[Res.r[3]][0] not in dict_d:
                    dict_d[data[Res.r[3]][0]] = 0
                else:
                    pass
                check_count += 1
                if data[Res.r[3]][1] == check_value:
                    dict_d[data[Res.r[3]][0]] += 1
                else:
                    pass
                if dict_d.__len__() > 1:
                    max_count_h = max_count * dict_d.__len__()
                else:
                    max_count_h = max_count
                if check_count >= max_count_h:
                    for i in dict_d:
                        if dict_d[i] == max_count:
                            q_out.put({Res.r[1]: head, Res.r[2]: data[Res.r[2]], Res.r[3]: [i, check_value]})
                        else:
                            if send_all_circles is True:
                                q_out.put({Res.r[1]: head, Res.r[2]: data[Res.r[2]], Res.r[3]: [i, not check_value]})
                            else:
                                pass
                    dict_d = {}
                    check_count, catch_count = 0, 0
                else:
                    pass

    # Checking the list of processes for compliance with the activity status
    @staticmethod
    def check_proc_list(q_in, q_out):
        while True:
            if q_in.empty() is False:
                data = q_in.get()
                if data[1] == Res.ProcDict[data[0]]:
                    state = True
                else:
                    state = False
                q_out.put({Res.r[2]: Res.K[1], Res.r[3]: [data[0], state]})
            else:
                time.sleep(1)

    # Send queue processing
    @staticmethod
    def to_send(data, q_out):
        data[Res.r[0]] = Res.M[0]
        q_out.put(data)

    # Internal queue processing
    @staticmethod
    def internal(q_internal, q_ua_valid, q_db_write, q_set_flag, q_send_mail, q_power_manager=None):
        while True:
            data = q_internal.get()
            # Agent check
            if data[Res.r[1]] == Res.H[2]:
                if data[Res.r[2]] == Res.K[7]:
                    q_ua_valid.put(data[Res.r[3]])
            # Write to the database
            if data[Res.r[1]] == Res.H[3]:
                if data[Res.r[2]] == Res.K[8]:
                    q_db_write.put(data[Res.r[3]])
            # Set flags
            if data[Res.r[1]] == Res.H[4]:
                q_set_flag.put({Res.r[2]: data[Res.r[2]],
                                Res.r[3]: data[Res.r[3]], }, )
            # Send Mail
            if data[Res.r[1]] == Res.H[5]:
                q_send_mail.put(data[Res.r[3]])
            if data[Res.r[2]] == Res.K[13]:
                q_power_manager.put(data)

    @staticmethod
    def set_flag(q_set_flag, q_controller, q_power_manager_flag):
        while True:
            data = q_set_flag.get()
            if data[Res.r[2]] == Res.K[9]:
                q_power_manager_flag.put(data[Res.r[3]])
            if data[Res.r[2]] == Res.K[10]:
                q_controller.put({Res.r[0]: Res.M[0], Res.r[1]: Res.H[4],
                                  Res.r[2]: Res.K[10], Res.r[3]: data[Res.r[3]]})
