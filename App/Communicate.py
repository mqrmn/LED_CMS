import socket
import time
import pickle

from App.Config import Config

class _Network_:

    def Server(self, host, port, Q_):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen(2)
            # Цикл прослушивания сокета
            while True:
                conn, addr = s.accept()
                # Действие при соединении с сервером
                with conn:
                    # Прием данных соединения
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        Q_.put(pickle.loads(data))


    def Client(self, host, port, Q_in, ):
        while True:
            data = Q_in.get()

            self.Send(host, port, data)

    def Send(self, host, port, data):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as Socket:
                Socket.connect((host, port))
                Socket.sendall(pickle.dumps(data))


