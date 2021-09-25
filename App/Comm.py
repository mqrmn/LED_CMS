# 1.1.1

import sys
import socket
import pickle
import time

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import Log

LOG = Log.LogManager()


class Socket:

    @staticmethod
    def server(host, port, q_out):
        LOG.cms_logger('Called')
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None) as s:
            s.bind((host, port))
            s.listen(10)
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
                        q_out.put(pickle.loads(data))
                    conn.close()

    def client(self, host, port, q_in, ):
        LOG.cms_logger('Called')
        while True:
            data = q_in.get()
            attempt = 0
            result = None
            while (result is not True) and attempt < 3:
                attempt += 1
                result = self.send(host, port, data)
                if result is not True:
                    time.sleep(3)

    @staticmethod
    def send(host, port, data):
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None) as SOCKET:
            try:
                SOCKET.connect((host, port))
                SOCKET.sendall(pickle.dumps(data))
                SOCKET.close()
                return True
            except:
                LOG.cms_logger(sys.exc_info()[1])
                return False
