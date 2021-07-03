# Echo client program
import socket
import time
HOST = 'localhost'    # The remote host
PORT = 50007              # The same port as used by the server

while True:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'Hello, worldddd')
            data = s.recv(1024)
        print('conn ok: ', 'Received', repr(data))
    except:
        print('conn fail')

    time.sleep(10)