# 1.1.1

import sys
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App.Config import Config
from App import Log

LOG = Log.LogManager()
LOG.cms_logger('CALLED')

global addr_from


class Mail:

    def __init__(self):

        global addr_from
        addr_from = Config.smtpSender

    @staticmethod
    def init_msg(messagetext):

        msg = MIMEMultipart()
        msg['From'] = addr_from
        msg['To'] = Config.smtpReceiver
        msg['Subject'] = Config.objType + ' ' + Config.objCode
        body = ('''
                {}
                Машина: {}
                Объкт: {}
                Номер салона: {}
                Адрес: {}
                '''.format(messagetext, socket.gethostname(), Config.objType, Config.objCode, Config.objAddress))
        msg.attach(MIMEText(body, 'plain'))

        return msg

    @staticmethod
    def init_server():

        server = smtplib.SMTP(Config.smtpServer, Config.smtpPort)
        server.starttls()
        server.login(Config.smtpSender, Config.smtpPass)

        return server

    def send_mail(self, messagetext):

        server = self.init_server()
        server.send_message(self.init_msg(messagetext))
        server.quit()

    def send_mail_controller(self, q_in):

        while True:
            messagetext = q_in.get()
            self.send_mail(messagetext)
