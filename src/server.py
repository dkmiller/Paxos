import logging as LOG
import os
import sys
from socket import SOCK_STREAM, socket, AF_INET
from threading import Thread, Lock

from replica import Replica

root_port = 20000
address = 'localhost'

class MasterHandler(Thread):
    def __init__(self, address, port):
        Thread.__init__(self)
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock,bind((address, port))
        self.sock.listen(1)
        slef.conn, self.addr = self.sock.accept()

    def run(self):
        while True:
            try:
                data = self.conn.recv(1024)
                if data:
                    data = data.split('\n')
                    data = data[:-1]


def main():
    pid = int(sys.argv[1]) # This server's id, from 0..N-1
    N = int(sys.argv[2]) # Total number of servers.
    port = int(sys.argv[3]) # Port number the server should listen on.

    LOG.basicConfig(filename=str(pid) + '.log', level=LOG.DEBUG)
    LOG.debug('pid: %d' % pid)
    
    replica = Replica(pid)
    LOG.debug('Replica()')

if __name__ == "__main__":
    main()
