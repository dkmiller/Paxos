import logging as LOG
import os
from Queue import Queue
from replica import Replica
import sys
from socket import SOCK_STREAM, socket, AF_INET
from threading import Thread, Lock

incoming = {}
N = None
pid = None
port = None
receive_threads = {}
send_thread = None
root_port = 20000
address = 'localhost'
mhandler = None

# TODO: make thread-safe.
def new_instance(kind):
    global incoming, pid, send, send_master
    subid = None

    if kind in ['acceptor', 'leader', 'master', 'replica', 'scout']:
        subid = kind
    elif kind == 'commander':
        if len(incoming) > 0:
            subid = max([i for i in incoming.keys() if isinstance(i, int)]) + 1
        else:
            subid = 0
        subid = str(subid)
    incoming[subid] = Queue()
    # Syntax: sender, msg = receive()
    def my_receive():
        LOG.debug('my_receive called')
        m = incoming[subid].get(block=True).split(':',4)
        sender = (int(m[0]), m[1])
        msg = m[4]
        LOG.debug('received: ' + msg)
        return (sender, msg)
    def my_send(recipient, msg):
        recipient_pid, recipient_subid = recipient
        if recipient_subid == 'master':
            send_master(msg)
        else:
            header = '%d:%s:%d:%s:' % (pid, subid, recipient_pid, recipient_subid)
            msg_to_send = header + msg
            LOG.debug('send: ' + msg_to_send)
            send(recipient_pid, msg_to_send)
    return (my_send, my_receive)

class ListenThread(Thread):
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        LOG.debug("Listen Handler inited")

    def run(self):
        global incoming
        LOG.debug("Listen Running")
        while True:
            try:
                data = self.conn.recv(1024)
                if data != "":
                    data = data.split('\n')
                    data = data[:-1]
                    for line in data:
                        LOG.debug("ListenThread: " + str(line))
                        # Give replica to the local replica.
                        recipient_subid = line.split(':', 4)[3]
                        # Message is to a commander.
                        if recipient_subid not in ['acceptor', 'leader', 'master', 'replica', 'scout']:
                            recipient_subid = int(recipient_subid)
                        msg = ls[4]
                        # Only pass on message if it is to a valid recipient. 
                        if recipient_subid in incoming:
                            incoming[recipient_subid].put(line)
            except:
                break

class WorkerThread(Thread):
    def __init__(self, address, internal_port, pid):
        Thread.__init__(self)
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((address, internal_port))
        self.sock.listen(1)
        LOG.debug("Worker Handler inited")

    def run(self):
        LOG.debug("Worker Running")
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
        LOG.debug('Master Handler inited')

    def run(self):
        global incoming
        LOG.debug("Master Running")
        while True:
            try:
                data = self.conn.recv(1024)
                if data:
                    data = data.split('\n')
                    data = data[:-1]
                    for line in data:
                        LOG.debug("MasterHandler: " + str(line))
                        header = '%d:%s:%d:%s:' % (self.port, 'master', -1, 'replica')
                        incoming['replica'].put(line)
            except:
                LOG.debug("ERROR: " + str(sys.exec_info()))
                self.sock.close()
                break

    def send(self, s):
        self.conn.send(str(s) + '\n')

    def close(self):
        try:
            self.sock.close()
        except:
            pass

def send_master(msg):
    global mhandler
    mhandler.send(str(msg) + '\n')
    LOG.debug("SOCKET: Master sending")

def send(pid, msg):
    try:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((address, root_port + pid))
        sock.send(str(msg) + '\n')
        sock.close()
        LOG.debug("SOCKET: sending")
    except:
        LOG.debug("SOCKET: ERROR")

def main():
    global N, pid, port

    # Read global state.
    pid = int(sys.argv[1])
    N = int(sys.argv[2])
    port = int(sys.argv[3])
    
    # Start debugger
    LOG.basicConfig(filename="LOG/" + str(pid) + '.log', level=LOG.DEBUG)
    
    LOG.debug('IDENTITY pid: %d, port: %d ' % (pid, port))

    # Create the replica running on this process.
    leaders = [(root_port + i, 1) for i in xrange(N)]

    # Spawn the replica.
    replica = Replica(leaders, '', new_instance)
    replica.start()

    # Spawn Master Thread to listen from master
    mhandler = MasterHandler(pid, address, port)
    mhandler.start()

    # Spawn All incoming connection threads
    handler = WorkerThread(address, root_port+pid, pid)
    handler.start()

    LOG.debug('main ends')

if __name__ == "__main__":
    main()

