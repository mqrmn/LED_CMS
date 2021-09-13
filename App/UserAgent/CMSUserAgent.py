# 1.1.1

import sys
import threading
import queue
from multiprocessing import Process, Queue

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config
from App import Comm, Handler, Control, Log
from App import Resource as Res

LOG = Log.Log_Manager()


def main(q_external):
    q_valid_screen_raw = queue.Queue()
    q_from_core = queue.Queue()
    q_to_send = queue.Queue()
    q_proc_state_raw = queue.Queue()
    q_proc_state = queue.Queue()
    q_prepare_to_send = queue.Queue()
    q_action = queue.Queue()
    q_control = queue.Queue()

    LOG.CMSLogger('Queues created')

    o_handlers = Handler.Queue()
    o_network = Comm.Socket()
    o_handler = Handler.Queue()
    o_control = Control.CMS()

    LOG.CMSLogger('Instances of classes created')

    t_server = threading.Thread(target=o_network.server,
                                args=(Config.localhost, Config.CMSUserAgentPort, q_from_core,))
    t_client = threading.Thread(target=o_network.client,
                                args=(Config.localhost, Config.CMSCoreInternalPort, q_to_send))
    t_prepare_to_send = threading.Thread(target=o_handlers.SendController,
                                         args=(q_prepare_to_send, q_to_send,))
    t_check_proc = threading.Thread(target=o_handler.CheckProcList,
                                    args=(q_proc_state_raw, q_proc_state))
    t_get_proc_state = threading.Thread(target=o_control.get_process_state,
                                        args=(q_proc_state_raw,))
    t_get_screen = threading.Thread(target=o_control.get_screen_static,
                                    args=(q_valid_screen_raw,))
    t_from_core = threading.Thread(target=o_handlers.FromCore,
                                   args=(q_from_core, q_action))
    t_action_run = threading.Thread(target=o_handlers.UAAction,
                                    args=(q_action, q_control))
    t_check_screen = threading.Thread(target=o_handlers.Valid,
                                      args=(q_valid_screen_raw,
                                            q_prepare_to_send, True, 2, Res.H[0], True,))
    t_valid_proc = threading.Thread(target=o_handler.Valid,
                                    args=(q_proc_state,
                                          q_prepare_to_send, False, 1, Res.H[0], True,))
    t_thread_control = threading.Thread(target=o_control.thread,
                                        args=(q_control, [t_server, t_client, t_action_run,
                                                          t_get_screen, t_check_screen,
                                                          t_get_proc_state, t_check_proc,
                                                          t_valid_proc, t_prepare_to_send,
                                                          t_from_core, ],))

    LOG.CMSLogger('Threads are initialized')

    t_server.start()
    t_client.start()
    t_action_run.start()
    t_get_screen.start()
    t_check_screen.start()
    t_get_proc_state.start()
    t_check_proc.start()
    t_valid_proc.start()
    t_from_core.start()
    t_prepare_to_send.start()
    t_thread_control.start()

    LOG.CMSLogger('Threads started')

    while True:
        _d = q_control.get()
        q_external.put(_d)


if __name__ == '__main__':
    Q_External = Queue()
    proc = Process(target=main, args=(Q_External,))
    proc.start()
    LOG.CMSLogger('Process started')

    while True:
        data = Q_External.get()
        if data == Res.TerminateThread[0]:
            proc.kill()
            LOG.CMSLogger('Process terminated')
            break
        else:
            pass
