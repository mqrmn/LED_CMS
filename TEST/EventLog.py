
import win32evtlog
import win32evtlogutil
import win32con
import winerror
import time

import re

import datetime

def TEST():
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    evt_dict = {win32con.EVENTLOG_INFORMATION_TYPE: 'EVENTLOG_INFORMATION_TYPE',
                win32con.EVENTLOG_WARNING_TYPE: 'EVENTLOG_WARNING_TYPE',
                win32con.EVENTLOG_ERROR_TYPE: 'EVENTLOG_ERROR_TYPE'}

    computer = None
    logtype = 'Microsoft-Windows-Kernel-Boot'
    # logtype = 'Application'
    begin_sec = time.time()
    begin_time = time.strftime('%H:%M:%S  ', time.localtime(begin_sec))

    hand = win32evtlog.OpenEventLog(computer, logtype)
    # print(logtype, ' events found in the last 8 hours since:', begin_time)

    list_ex_1 = ['Netwtw08', 'DCOM', 'Microsoft-Windows-DNS-Client', 'Microsoft-Windows-WindowsUpdateClient',
            'Microsoft-Windows-Kernel-General', 'Microsoft-Windows-NDIS', 'Microsoft-Windows-Power-Troubleshooter',
            'Microsoft-Windows-Time-Service', 'BTHUSB', 'Service Control Manager', 'Microsoft-Windows-DHCPv6-Client',
            'Microsoft-Windows-Dhcp-Client', 'Microsoft-Windows-Kernel-Processor-Power', 'Microsoft-Windows-FilterManager',
            'Microsoft-Windows-Ntfs', 'Microsoft-Windows-Directory-Services-SAM', ]

    list_ex_2 = ['Software Protection Platform Service', 'SecurityCenter', 'Microsoft-Windows-Perflib', 'ESENT', 'igfxCUIService2.0.0.0',
                 'gupdate', 'Wlclntfy', 'igccservice', 'Windows Search Service', 'Microsoft-Windows-PerfNet', 'Microsoft-Windows-PerfProc',
                 'RtkAudioUniversalService', 'Microsoft-Windows-WMI', 'CMSController', 'CMS', 'VSS', 'System Restore' ]

    list_1 = ['Microsoft-Windows-User Profiles Service', 'Microsoft-Windows-RestartManager', ]

    list_2 = ['User32', 'Microsoft-Windows-Winlogon', 'Microsoft-Windows-Kernel-Power', 'Microsoft-Windows-Kernel-Boot',
              'EventLog', 'Kernel-Boot']

    events = 1
    from App import Database

    table = Database.Tables()

    currentRun = table.SystemRun().select().order_by(table.SystemRun.id.desc()).get()
    lastInit = table.SystemInit().select().order_by(table.SystemInit.id.desc()).get()
    lastReboot = table.SelfInitShutdown().select().order_by(table.SelfInitShutdown.id.desc()).get()

    PREcurrentRun = table.SystemRun().select().where(table.SystemRun.id == currentRun.id - 1).get()

    # print('currentRun:', currentRun.id, currentRun.datetime)
    # print('lastInit:', lastInit.id, lastInit.datetime)
    # print('lastReboot:', lastReboot.id, lastReboot.datetime)
    #
    # print()
    # print('PREcurrentRun', PREcurrentRun.id, PREcurrentRun.datetime)

    timeLine = (datetime.datetime.now() - PREcurrentRun.datetime).seconds

    # print(timeLine)

    if lastReboot.id != PREcurrentRun.id:
        print('ПРЕДЫДУЩЕЕ ОТКЛЮЧЕНИЕ НЕ БЫЛО ИНИЦИИРОВАНО CMS')
        while events:
            try:
                events = win32evtlog.ReadEventLog(hand, flags, 0)
                for ev_obj in events:

                    the_time = ev_obj.TimeGenerated
                    if (datetime.datetime.now() - the_time).seconds <= timeLine:

                        if str(ev_obj.SourceName) in list_2:
                            cat = str(ev_obj.EventCategory)
                            src = str(ev_obj.SourceName)
                            evt_type = str(evt_dict[ev_obj.EventType])
                            msg = str(win32evtlogutil.SafeFormatMessage(ev_obj, logtype))
                            evt_id = str(winerror.HRESULT_CODE(ev_obj.EventID))
                            # print((the_time.Format(), ':', src, cat, evt_id, evt_type, msg))

                            if src == 'User32' and evt_id == '1074':
                                print((the_time.Format(), ':', src, evt_id, msg))
                                print('ВОЗМОЖНО СИСТЕМА БЫЛА ПЕРЕЗАГРУЖЕНА ПОЛЬЗОВАТЕЛЕМ, '
                                      'ВРЕМЯ СОБЫТИЯ: {}'.format(the_time.Format()))
                            # re.findall(r'\d{4}-\d{2}-\d{2}', msg)

            except:
                print('EXC')
        win32evtlog.CloseEventLog(hand)

if __name__ == '__main__':
    TEST()