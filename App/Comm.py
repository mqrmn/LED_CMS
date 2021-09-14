# 1.1.1

import sys
import socket
import pickle

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import Log

LOG = Log.LogManager()


class Socket:

    @staticmethod
    def server(host, port, q_):
        LOG.cms_logger('Called')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen(2)
            # Socket listening loop
            while True:
                conn, addr = s.accept()
                # Action when connecting to a server
                with conn:
                    # Receiving connection data
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break

                        q_.put(pickle.loads(data))

    def client(self, host, port, q_in, ):
        LOG.cms_logger('Called')
        while True:
            data = q_in.get()
            self.send(host, port, data)

    @staticmethod
    def send(host, port, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as SOCKET:
            try:
                SOCKET.connect((host, port))
                SOCKET.sendall(pickle.dumps(data))
            except:
                LOG.cms_logger('CONNECTION ERROR')
