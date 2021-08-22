# 1.1.1

import sys
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config


def sendmail(messagetext):
    addr_from = 'notification.ktk@yandex.ru'
    addr_to = 'alex.s@znp74.ru'
    password = 'FMV:m53FNPT1'
    msg = MIMEMultipart()
    msg['From'] = addr_from
    msg['To'] = addr_to
    msg['Subject'] = Config.objType + ' ' + Config.objCode
    body = ('''{}
            
Машина: {}
Объкт: {}
Номер салона: {}
Адрес: {}'''.format(messagetext, socket.gethostname(), Config.objType, Config.objCode, Config.objAddress))
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.yandex.ru', 587)
    # server.set_debuglevel(True)
    server.starttls()
    server.login(addr_from, password)
    server.send_message(msg)
    server.quit()