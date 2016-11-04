import logging as LOG
import os
from Queue import Queue
from replica import Replica
import sys
from socket import SOCK_STREAM, socket, AF_INET
from threading import Thread, Lock

incoming = {}
incoming_lock = None
N = None
pid = None
port = None
receive_threads = {}
send_thread = None
root_port = 20000
address = 'localhost'
mhandler = None

class Communicator:
    def __init__(self, incoming, incoming_lock, pid, send, send_master):
        self.commander_seq = 0
        self.incoming = incoming
        self.incoming_lock = incoming_lock
        self.pid = pid
        self.send = send
        self.send_master = send_master
    def build(self, kind):
        with self.incoming_lock:
            if kind == 'commander':
                subid = self.commander_seq
                commander_seq += 1
            else:
                subid = kind
            LOG.debug('subid = ' + str(subid))
            if subid not in self.incoming:
                self.incoming[subid] = Queue()
            LOG.debug('self.incoming = %s' % str(self.incoming))

        # Syntax: sender, message = receive().
        def my_receive():
            LOG.debug('%d: receive() called' % self.pid)
            # Blocks until a message is ready.
            content = self.incoming[subid].get(block=True).split(':',4)
            sender = (int(content[0]),content[1]) # (port, subid)
            # Skip recipient port, subid.
            message = content[4]
            LOG.debug('%d: receive message: %s' % (self.pid, message))
            return (sender, message)
        LOG.debug('defined my_receive()')
        def my_send(recipient, message):
            recipient_pid, recipient_subid = recipient
            if recipient_subid == 'master':
                self.send_master(message)
            else:
                header = '%d:%s:%d:%s:' % (self.pid, str(subid), recipient_pid, recipient_subid)
                send_message = header + message
                LOG.debug('send: %s' % send_message)
                self.send(recipient_pid, send_message)
        LOG.debug('about to return (my_send, my_receive)')
        return (my_send, my_receive)

class ListenThread(Thread):
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.buffer = ''
        self.valid = True
        LOG.debug("Listen Handler inited")

    def run(self):
        global incoming, incoming_lock
        LOG.debug("Listen Running")
        while self.valid:
            if '\n' in self.buffer:
                (line, rest) = self.buffer.split('\n',1)
                self.buffer = rest
                LOG.debug('ListenThread: received %s' % str(line))
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
        self.port = port
        self.buffer = ''
        self.valid = True
        LOG.debug('MasterHandler init')

    def run(self):
        global incoming, incoming_lock
        LOG.debug('MasterHandler Running')
        while self.valid:
            if '\n' in self.buffer:
                (line, rest) = self.buffer.split('\n', 1)
                self.buffer = rest
                header = '%d:%s:%d:%s:' % (-1, 'master', self.index, 'replica')
                line = header + line
                LOG.debug('received %s' % line)
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
    global incoming, incoming_lock, N, pid, port, send, send_master

    # Read global state.
    pid = int(sys.argv[1])
    N = int(sys.argv[2])
    port = int(sys.argv[3])
    
    # Start debugger
    LOG.basicConfig(filename="LOG/" + str(pid) + '.log', level=LOG.DEBUG)
    
    LOG.debug('IDENTITY pid: %d, port: %d ' % (pid, port))

    # Create the replica running on this process.
    leaders = [(root_port + i, 1) for i in xrange(N)]

    incoming_lock = Lock()
    communicator = Communicator(incoming, incoming_lock, pid, send, send_master)
    LOG.debug('created communicator')

    # Spawn the replica.
    replica = Replica(leaders, '', communicator)
    LOG.debug('created replica')
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

