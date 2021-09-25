# 1.1.1

import sys
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config as Con
from App import Log

LOG = Log.LogManager()
LOG.cms_logger('CALLED')

global addr_from


class Mail:

    def __init__(self):

        global addr_from
        addr_from = Con.smtpSender

    @staticmethod
    def init_msg(messagetext):

        msg = MIMEMultipart()
        msg['From'] = addr_from
        msg['To'] = Con.smtpReceiver
        msg['Subject'] = Con.objType + ' ' + Con.objCode
        body = ('''
                {}
                Машина: {}
                Объкт: {}
                Номер салона: {}
                Адрес: {}
                '''.format(messagetext, socket.gethostname(), Con.objType, Con.objCode, Con.objAddress))
        msg.attach(MIMEText(body, 'plain'))

        return msg

    @staticmethod
    def init_server():

        server = smtplib.SMTP(Con.smtpServer, Con.smtpPort)
        server.starttls()
        server.login(Con.smtpSender, Con.smtpPass)

        return server

    def send_mail(self, messagetext):

        server = self.init_server()
        server.send_message(self.init_msg(messagetext))
        server.quit()

    def send_mail_controller(self, q_send_mail):

        while True:
            messagetext = q_send_mail.get()
            self.send_mail(messagetext)
