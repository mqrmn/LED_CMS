# 1.1.1

import sys
import socket
import pickle

sys.path.append("C:\\MOBILE\\Local\\CMS")

from App import Log

LOG = Log.Log_Manager()


class Socket:

    def Server(self, host, port, Q_):
        LOG.CMSLogger('Called')
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

                        Q_.put(pickle.loads(data))


    def Client(self, host, port, Q_in, ):
        LOG.CMSLogger('Called')
        while True:
            data = Q_in.get()
            self.Send(host, port, data)

    def Send(self, host, port, data):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as Socket:
                try:
                    Socket.connect((host, port))
                    Socket.sendall(pickle.dumps(data))
                except:
                    LOG.CMSLogger('CONNECTION ERROR')


