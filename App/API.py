# 1.1.1

import sys
import wmi
import pythoncom
import time
import psutil

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import Log
from App import Resource as Res
LOG = Log.LogManager()


class Win:

    @staticmethod
    def coin_init():
        pythoncom.CoInitialize()

    def get_wmi(self, privileges=None):
        self.coin_init()
        handle = wmi.WMI(privileges=privileges)
        return handle


class Process(Win):

    def get_proc_state(self, i):
        return self.get_wmi().Win32_Process(Name=i)

    def get_process_state(self, q_out):
        for i in Res.ProcDict:
            if self.get_proc_state(i):
                proc_state = True
            else:
                proc_state = False
            q_out.put([i, proc_state])

    def start_proc(self, executable):
        self.get_wmi().Win32_Process.Create(CommandLine=executable, )

    def terminate_proc(self, name):
        for proc in self.get_wmi().Win32_Process(Name=name):
            try:
                proc.terminate(Reason=1)
            except TypeError:
                pass
            except:
                LOG.cms_logger(sys.exc_info()[1])


class Service(Win):

    def get_service(self, name):
        LOG.cms_logger('Called')
        if name:
            return self.get_wmi().Win32_Service(name=name)[0]

    def stop_service(self, name):
        LOG.cms_logger('Called')
        return self.get_service(name).stop_service()

    def start_service(self, name):
        LOG.cms_logger('Called')
        return self.get_service(name).start_service()

    def get_service_state(self, name):
        LOG.cms_logger('Called')
        return self.get_service(name).State


class System(Win):

    def restart_pc(self):
        LOG.cms_logger('Called')
        self.get_wmi(["Shutdown"]).Win32_OperatingSystem()[0].Reboot()

    def shutdown_pc(self):
        LOG.cms_logger('Called')
        self.get_wmi(["Shutdown"]).Win32_OperatingSystem()[0].Shutdown()


class Nova(Process):

    def restart_nova(self):
        LOG.cms_logger('Called')
        self.terminate_nova()
        self.run_nova()

    def run_nova(self):
        LOG.cms_logger('Called')
        executable = 'C:\\Program Files (x86)\\NovaStudio\\Bin\\NovaStudio.exe'
        self.start_proc(executable)

    def terminate_nova(self):
        LOG.cms_logger('Called')
        self.terminate_proc(Res.ProcList[0])

    def terminate_mars(self):
        LOG.cms_logger('Called')
        executable = 'C:\\Users\\rAdmin_local\\AppData\\Roaming\\Nova Star\\NovaLCT\\Bin\\NovaLCT.exe'
        self.start_proc(executable)

        time.sleep(15)
        for proc in psutil.process_iter():
            process_name = proc.as_dict(attrs=['name'])
            process_pid = proc.as_dict(attrs=['pid'])
            if process_name['name'] == 'NovaLCT.exe':

                nova_process = psutil.Process(process_pid['pid'])
                for child in nova_process.children(recursive=True):
                    child.kill()

                nova_process.kill()

            else:
                pass
