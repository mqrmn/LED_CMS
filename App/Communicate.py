import socket
from App.Config import Config

class Network:

    def Server(self, host, port, dataQueue):
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
                    dataQueue.put(dataArr)



    def Client(self, host, port, data):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            for d in data:
                s.sendall(str(d).encode())
                dataRecv = s.recv(1024)

