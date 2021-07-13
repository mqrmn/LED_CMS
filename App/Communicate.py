import socket
import time

from App.Config import Config

class _Network_:

    def Server(self, host, port, Q_):
        print('RUN SERVER', host, port,)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen(2)
            # Цикл прослушивания сокета
            while True:

                conn, addr = s.accept()

                # Действие при соединении с сервером
                with conn:
                    dataArr = []
                    # Прием данных соединения
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        dataArr.append(data.decode())
                        conn.sendall(data)
                    Q_.put(dataArr)
                    # print('Server', dataArr)

    def Client(self, host, port, Q_, ):
        while True:
            if Q_.empty() == False:
                data = Q_.get()
                self.Send(host, port, data)
            else:
                time.sleep(3)


    def Send(self, host, port, data):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as Socket:
            Socket.connect((host, port))
            for d in data:
                Socket.sendall(str(d).encode())
                dataRecv = Socket.recv(1024)

