# 1.1.1

import sys
import numpy as np
import pyautogui
import cv2
import random
import time
import datetime
import threading
import socket
import schedule
from inspect import currentframe, getframeinfo

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config as Con
from App import Valid, API, Act, Log, Database
from App import Resource as Res


LOG = Log.LogManager()

global o_CrMsg


class Init:
    def __init__(self):
        global o_CrMsg
        o_CrMsg = Res.CreateMessage()


class CMS(Init):

    @staticmethod
    def scheduler():
        c_action_sys = Act.System()
        schedule.every().day.at(Con.shutdown_time).do(c_action_sys.reboot_init)
        while True:
            schedule.run_pending()
            time.sleep(1)


    @staticmethod
    def thread(q_in, data):
        while True:
            if q_in.empty() is False:
                q_data = q_in.get()
                if q_data == Res.TerminateThread[0]:
                    break
            c_valid = Valid.System()
            th_states = c_valid.threads(data)
            if False in th_states:
                pass
            time.sleep(10)

    # Tracking UA status
    @staticmethod
    def ua_valid(q_ua_valid, q_internal):

        c_prepare = Database.Prepare()
        data = datetime.datetime.now()
        count = 0
        while True:
            if q_ua_valid.empty() is False:
                data = q_ua_valid.get()
                if count == 0:
                    q_internal.put(c_prepare.system_init_prep(datetime.datetime.now()))
                    count += 1
            else:
                if (datetime.datetime.now() - data).seconds >= Con.ua_delay:
                    q_internal.put(o_CrMsg.reboot_system())

            time.sleep(3)

    # Checking the screen for static
    @staticmethod
    def get_screen_static(q_valid_screen_raw):
        ch_sum_arr = []
        if Con.screenNum == 1:
            while True:
                while len(ch_sum_arr) < 2:
                    screen_shot = pyautogui.screenshot(region=(Con.regiondict[0]))
                    ch_int = cv2.cvtColor(np.array(screen_shot), cv2.COLOR_RGB2BGR)
                    common_int = ch_int.sum(axis=2)
                    ch_sum = np.sum(common_int)
                    if len(ch_sum_arr) < 2:
                        ch_sum_arr.append(ch_sum)

                # Checking values, passing the result to the queue
                if len(ch_sum_arr) == 2:
                    if ch_sum_arr[0] == ch_sum_arr[1]:  # Screen is static
                        q_valid_screen_raw.put({Res.r[2]: Res.K[0],
                                                Res.r[3]: [Res.ScreenState[0], True], })
                    else:
                        q_valid_screen_raw.put({Res.r[2]: Res.K[0],
                                                Res.r[3]: [Res.ScreenState[0], False], })
                    del ch_sum_arr[0]  # Remove entry with index 0 from the dictionary
                time.sleep(random.randint(Con.timeoutSCheck[0], Con.timeoutSCheck[1]))
        else:
            pass

    # Checking the status of selected processes
    @staticmethod
    def get_process_state(q_proc_state_raw):
        c_win_api = API.Process()
        while True:
            t_get_process_state = threading.Thread(target=c_win_api.get_process_state, args=(q_proc_state_raw,))
            t_get_process_state.start()
            t_get_process_state.join()
            time.sleep(Con.timeoutPCheck)

    @staticmethod
    def cms_service(q_manage, q_from_updater, ):
        c_action_sys = Act.System()
        c_action_init = Act.SysInit()
        table = Database.Tables()
        flag = c_action_init.check_last_self_init_std(q_manage)

        while True:
            time.sleep(Con.cms_service_delay)
            if q_manage.empty() is False:
                flag = q_manage.get()[Res.r[3]]

                LOG.cms_logger('Reboot control flag: {}'.format(flag))

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as Socket:
                try:
                    Socket.connect((Con.localhost, Con.CMSCoreInternalPort))
                    LOG.cms_logger('CMS Run', )
                except:
                    if q_from_updater.empty() is False:
                        if q_from_updater.get() is True:
                            LOG.cms_logger('CMS Stopped for upgrade', )
                            break
                        else:
                            pass
                    else:
                        LOG.cms_logger('CMS Stopped', )
                        if flag > 0:
                            if flag > 1:

                                LOG.cms_logger('Reboot scheduled')
                                c_action_sys.reboot_init()

                                break
                            else:

                                last_reboot = table.SelfInitShutdown().select().order_by(
                                    table.SelfInitShutdown.id.desc()).get()
                                if (datetime.datetime.now() - last_reboot.datetime).seconds >= Con.cont_last_reb_delay:

                                    LOG.cms_logger('Reboot scheduled')
                                    c_action_sys.reboot_init()
                                    break
                                else:
                                    LOG.cms_logger('Restart access denied')
                        else:
                            LOG.cms_logger('Restart access denied')

    @staticmethod
    def power_manager(q_power_manager, q_internal, q_power_manage_flag):

        c_action = Act.System()

        c_prepare = Database.Prepare()
        table = Database.Tables()
        while True:
            flag = q_power_manage_flag.get()
            LOG.cms_logger('Reboot control flag: {}'.format(flag))
            data = q_power_manager.get()
            LOG.cms_logger('Power manager received data: {}'.format(data))

            if data:

                if flag > 0:
                    if flag > 1:

                        q_internal.put(c_prepare.self_init_shutdown_prep(getframeinfo(currentframe())[2], 'reboot',
                                                                         datetime.datetime.now()))
                        LOG.cms_logger('Reboot scheduled')
                        c_action.reboot_init()
                        break
                    else:
                        last_reboot = table.SelfInitShutdown().select().order_by(table.SelfInitShutdown.id.desc()).get()
                        if (datetime.datetime.now() - last_reboot.datetime).seconds <= Con.last_reb_delay:

                            q_internal.put(c_prepare.self_init_shutdown_prep(getframeinfo(currentframe())[2], 'reboot',
                                                                             datetime.datetime.now()))
                            LOG.cms_logger('Reboot scheduled')
                            c_action.reboot_init()
                            break
                        else:
                            q_internal.put(
                                c_prepare.self_init_shutdown_prep(getframeinfo(currentframe())[2], 'rebootAccessDenied',
                                                                  datetime.datetime.now()))
                            LOG.cms_logger('Restart access denied')
                else:
                    q_internal.put(c_prepare.self_init_shutdown_prep(getframeinfo(currentframe())[2],
                                                                     'rebootAccessDenied',
                                                                     datetime.datetime.now()))
                    LOG.cms_logger('Restart access denied')
            else:
                pass
