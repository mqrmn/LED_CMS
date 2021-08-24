
from App import Log

import win32evtlog

import win32evtlogutil

import win32security

import win32con

import winerror

import time

import re

import string

import sys

import traceback
import datetime

def TEST():
    ####Main program

    # initialize variables
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

    # This dict converts the event type into a human readable form

    evt_dict = {win32con.EVENTLOG_INFORMATION_TYPE: 'EVENTLOG_INFORMATION_TYPE',
                win32con.EVENTLOG_WARNING_TYPE: 'EVENTLOG_WARNING_TYPE',
                win32con.EVENTLOG_ERROR_TYPE: 'EVENTLOG_ERROR_TYPE'}

    computer = None
    logtype = 'System'
    begin_sec = time.time()
    begin_time = time.strftime('%H:%M:%S  ', time.localtime(begin_sec))

    # open event log

    hand = win32evtlog.OpenEventLog(computer, logtype)
    print(logtype, ' events found in the last 8 hours since:', begin_time)

    try:
        events = 1
        while events:
            events = win32evtlog.ReadEventLog(hand, flags, 0)
            for ev_obj in events:

                # check if the event is recent enough

                # only want data from last 8hrs

                the_time = ev_obj.TimeGenerated


                if (datetime.datetime.now() - the_time).days <= 3:

                    # data is recent enough, so print it out

                    print(ev_obj)

                    computer = str(ev_obj.ComputerName)

                    cat = str(ev_obj.EventCategory)

                    src = str(ev_obj.SourceName)

                    record = str(ev_obj.RecordNumber)

                    evt_id = str(winerror.HRESULT_CODE(ev_obj.EventID))

                    evt_type = str(evt_dict[ev_obj.EventType])

                    msg = str(win32evtlogutil.SafeFormatMessage(ev_obj, logtype))

                    print((the_time.Format(), computer, src, cat, record, evt_id, evt_type, msg), ':' )


        win32evtlog.CloseEventLog(hand)

    except:
        print(traceback.print_exc(sys.exc_info()))

if __name__ == '__main__':
    TEST()