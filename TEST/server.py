import socket

HOST = 'localhost'                 # Symbolic name meaning all available interfaces
PORT = 50007              # Arbitrary non-privileged port


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(2)
    # Цикл прослушивания сокета
    while True:
        conn, addr = s.accept()
        # Действие при соединении с сервером
        with conn:

            print('Connected by', addr)
            # Прием данных соединения
            while True:
                data = conn.recv(1024)
                if not data: break
                print(data.decode())
                conn.sendall(data)
