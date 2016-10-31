import sys
from threading import Thread, Lock
from socket import SOCK_STREAM, socket, AF_INET

address = 'localhost'
index = -1
port = -1
threads = {}
N = 0

def log(msg):
    global index
    filename = 'log' + str(index) + '.log'
    with open(filename, 'a+') as f:
        f.write(msg)


class Replica(Thread):
    def __init__(self):
        global address, index, N, port, threads
        Thread.__init__(self)
        self.buffer = ""

        # Begin logging.
        log('begin %d' % str(index))

        # Listen to the master.
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((address, port))
        self.sock.listen(1)
        conn, addr = self.sock.accept()
        self.valid = True

        log('conn = %s' % str(conn))

    def run(self):
        global threads
        while self.valid:
            if '\n' in self.buffer:
                (line, rest) = self.buffer.split('\n', 1)
                self.buffer = rest
                log(line)
            else:
                try:
                    data = self.sock.recv(1024)
                    self.buffer += data
                except:
                    self.valid = False
                    del threads[-1]
                    self.sock.close()
                    break

def main():
    global index, N, port, threads
    index = int(sys.argv[1]) # This server's id, from 0..N-1
    N = int(sys.argv[2]) # Total number of servers.
    port = int(sys.argv[3]) # Port number the server should listen on.

    replica = Replica()
    threads[-1] = replica
    replica.start()

if __name__ == "__main__":
    main()
