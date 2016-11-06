import logging as LOG
import os
from Queue import Queue
from acceptor import Acceptor
from leader import Leader
from replica import Replica
import sys
from socket import SOCK_STREAM, socket, AF_INET
from threading import Thread, Lock

incoming = {}
incoming_lock = Lock()
N = None
pid = None
port = None
receive_threads = {}
send_thread = None
root_port = 20000
address = 'localhost'
mhandler = None

class Communicator:
    def __init__(self, incoming, incoming_lock, pid, send, mhandler):
        self.commander_seq = 0
        self.incoming = incoming
        self.incoming_lock = incoming_lock
        self.mhandler = mhandler
        self.pid = pid
        self.send = send
    # Returns an "identity" (pid, kind) for the calling thread.
    def identity(kind):
        return (self.pid, kind)
    def build(self, kind):
        with self.incoming_lock:
            if kind == 'commander':
                subid = self.commander_seq
                commander_seq += 1
            else:
                subid = kind
            if subid not in self.incoming:
                self.incoming[subid] = Queue()

        # Syntax: sender, message = receive().
        def my_receive():
            # Blocks until a message is ready.
            content = self.incoming[subid].get(block=True).split(':',4)
            sender = (int(content[0]),content[1]) # (port, subid)
            # Skip recipient port, subid.
            message = content[4]
            return (sender, message)
        def my_send(recipient, message):
            LOG.debug('sending: %s' % message)
            recipient_pid, recipient_subid = recipient
            if recipient_subid == 'master':
                self.mhandler.send(message)
            else:
                header = '%d:%s:%d:%s:' % (self.pid, str(subid), recipient_pid, recipient_subid)
                send_message = header + message
                self.send(recipient_pid, send_message)
        return (my_send, my_receive)

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
                LOG.debug('received: %s' % line)
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
    def __init__(self, address, internal_port, pid):
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
    try:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((address, root_port + pid))
        sock.send(str(msg) + '\n')
        sock.close()
    except:
        LOG.debug("SOCKET: ERROR")

def main():
    global incoming, incoming_lock, N, pid, port, send

    # Read global state.
    pid = int(sys.argv[1])
    N = int(sys.argv[2])
    port = int(sys.argv[3])
    
    # Start debugger
    LOG.basicConfig(filename="LOG/" + str(pid) + '.log', level=LOG.DEBUG)

    # Create the necessary classes.
    mhandler = MasterHandler(pid, address, port)
    handler = WorkerThread(address, root_port+pid, pid)
    communicator = Communicator(incoming, incoming_lock, pid, send, mhandler)

    acceptors = [(i, 'acceptor') for i in xrange(N)]
    leaders = [(i, 'leader') for i in xrange(N)]
    replicas = [(i, 'replica') for i in xrange(N)]
    acceptor = Acceptor(communicator)
    replica = Replica(leaders, '', communicator)
    leader = Leader(acceptors, replicas, communicator)

    LOG.debug('server: incoming = %s' % str(incoming))

    # Spawn Paxos threads.
    acceptor.start()
    leader.start()
    replica.start()
    # Spawn handler threads.
    mhandler.start()
    handler.start()

    LOG.debug('main() ends IDENTITY pid: %d, port: %d ' % (pid, port))

if __name__ == "__main__":
    main()

