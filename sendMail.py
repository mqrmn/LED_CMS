encoding="UTF-8"

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import socket
import config

def sendmail(messagetext):
    addr_from = 'notification.ktk@yandex.ru'    # Адресат
    addr_to = 'alex.s@znp74.ru'            # Получатель
    password = 'FMV:m53FNPT1'                   # Пароль
    msg = MIMEMultipart()                       # Создаем сообщение
    msg['From'] = addr_from                     # Адресат
    msg['To'] = addr_to                         # Получатель
    msg['Subject'] = config.objType + ' ' + config.objCode         # Тема сообщения
    body = ('''{}
            
Машина: {}
Объкт: {}
Номер салона: {}
Адрес: {}'''.format(messagetext, socket.gethostname(), config.objType, config.objCode, config.objAddress))
    msg.attach(MIMEText(body, 'plain'))         # Добавляем в сообщение текст
    server = smtplib.SMTP('smtp.yandex.ru', 587)        # Создаем объект SMTP
    # server.set_debuglevel(True)                        # Режим отладки
    server.starttls()                                   # Начинаем шифрованный обмен по TLS
    server.login(addr_from, password)                   # Получаем доступ
    server.send_message(msg)                            # Отправляем сообщение
    server.quit()