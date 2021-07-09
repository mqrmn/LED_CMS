import socket
from App.Config import Config

class Network:

    def Server(self, host, port, dataQueue):
        print('RUN SERVER', host, port,)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen(2)
            # Цикл прослушивания сокета
            while True:

                conn, addr = s.accept()
                print('CONN', conn, addr)
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

    def SendUserAgent(self,host, port, SendUserAgentQueue, ):
        while True:
            if SendUserAgentQueue.empty() == False:
                data = SendUserAgentQueue.get()
                if type(data) == list:
                    if data[0] == 'CoreScreenValidation':
                        if data[1] == '1':
                            self.Client(host, port, data)

            else:
                pass


    def Client(self, host, port, data):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            for d in data:
                s.sendall(str(d).encode())
                dataRecv = s.recv(1024)

