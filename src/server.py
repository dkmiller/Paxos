import logging as LOG
import os
from socket import SOCK_STREAM, socket, AF_INET
import sys
from threading import Thread, Lock
import time

# Application code.
from acceptor import Acceptor
from communicator import Communicator
from leader import Leader
from replica import Replica

# Global variables.
incoming = {} # Hashmap of queues of messages for different subids.
incoming_lock = Lock()
N = None # Number of processes.
pid = None # Process ID of this process.
port = None # Port number to listen on for master-communication.
receive_threads = {}
send_thread = None
root_port = 20000
address = 'localhost'
mhandler = None


class ListenThread(Thread):
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.buffer = ''
        self.valid = True

    def run(self):
        global incoming, incoming_lock
        while self.valid:
            if '\n' in self.buffer:
                (line, rest) = self.buffer.split('\n',1)
                LOG.debug('ListenThread.run: received: %s' % line)
                self.buffer = rest
                recipient_subid = line.split(':', 4)[3]
                try:
                    recipient_subid = int(recipient_subid)
                except ValueError:
                    pass
                with incoming_lock:
                    if recipient_subid in incoming:
                        incoming[recipient_subid].put(line)
            else:
                try:
                    data = self.conn.recv(1024)
                    self.buffer += data
                except:
                    LOG.debug("Listen handler recv failed")
                    self.valid = False
                    self.conn.close()
                    break
                

class WorkerThread(Thread):
    def __init__(self, address, internal_port):
        Thread.__init__(self)
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((address, internal_port))
        self.sock.listen(1)
    def run(self):
        while True:
            conn, addr = self.sock.accept()
            handler = ListenThread(conn, addr)
            handler.start()

class MasterHandler(Thread):
    def __init__(self, index, address, port):
        Thread.__init__(self)
        self.index = index
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((address, port))
        self.sock.listen(1)
        self.conn, self.addr = self.sock.accept()
        self.port = port
        self.buffer = ''
        self.valid = True
    def run(self):
        global incoming, incoming_lock
        while self.valid:
            if '\n' in self.buffer:
                (line, rest) = self.buffer.split('\n', 1)
                self.buffer = rest
                header = '%d:%s:%d:%s:' % (-1, 'master', self.index, 'replica')
                line = header + line
                if 'replica' in incoming:
                    incoming['replica'].put(line)
            else:
                try:
                    data = self.conn.recv(1024)
                    self.buffer += data
                except:
                    LOG.debug('MasterHandler error: %s' % str(sys.exec_info()))
                    self.valid = False
                    self.conn.close()
                    break
    def send(self, s):
        self.conn.send(str(s) + '\n')
    def close(self):
        try:
            self.sock.close()
        except:
            pass

def send(pid, msg):
    global root_port
    try:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((address, root_port + pid))
        sock.send(str(msg) + '\n')
        sock.close()
    except:
        LOG.debug('SOCKET: ERROR ' + str(msg))

def main():
    global incoming, incoming_lock, N, pid, port, root_port, send

    # Read global state.
    pid = int(sys.argv[1])
    N = int(sys.argv[2])
    port = int(sys.argv[3])

    
    # Start and configure debugger
    LOG.basicConfig(filename='LOG/%d.log' % pid, level=LOG.DEBUG)

    # Create the necessary classes.
    mhandler = MasterHandler(pid, address, port)
    handler = WorkerThread(address, root_port + pid)
    communicator = Communicator(incoming, incoming_lock, pid, send, mhandler)
    #LOG.debug('Handlers initiated')

    acceptors = [(i, 'acceptor') for i in xrange(N)]
    leaders = [(i, 'leader') for i in xrange(N)]
    replicas = [(i, 'replica') for i in xrange(N)]
    acceptor = Acceptor(communicator)
    my_dict = dict()
    replica = Replica(leaders, my_dict, communicator)
    leader = Leader(acceptors, replicas, communicator)

    acceptor.start()
    handler.start()
    mhandler.start()

    while not os.path.isfile('LOG/%d.log' % (N-1)):
        time.sleep(0.1)

    leader.start()
    replica.start()

    LOG.debug('main() ends IDENTITY pid: %d, port: %d ' % (pid, port))

if __name__ == "__main__":
    main()

