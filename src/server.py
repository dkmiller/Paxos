import logging as LOG
import os
from Queue import Queue
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
        self.send_master = send_master
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
            LOG.debug('my_send()')
            recipient_pid, recipient_subid = recipient
            if recipient_subid == 'master':
                self.mhandler.send(message)
                LOG.debug('sent %s to master' % message)
            else:
                header = '%d:%s:%d:%s:' % (self.pid, str(subid), recipient_pid, recipient_subid)
                send_message = header + message
                self.send(recipient_pid, send_message)
        LOG.debug('Connector.build()')
        return (my_send, my_receive)

class ListenThread(Thread):
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.buffer = ''
        self.valid = True
        LOG.debug("ListenHandler()")

    def run(self):
        global incoming, incoming_lock
        LOG.debug('ListenHandler.run()')
        while self.valid:
            if '\n' in self.buffer:
                (line, rest) = self.buffer.split('\n',1)
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
        LOG.debug('WorkerThread()')

    def run(self):
        LOG.debug('WorkerThread.run()')
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
        LOG.debug('MasterHandler()')

    def run(self):
        global incoming, incoming_lock
        LOG.debug('MasterHandler.run()')
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
        LOG.debug('MasterHandler.send(%s)' % s)
        self.conn.send(str(s) + '\n')
        LOG.debug('MasterHandler.send() complete')

    def close(self):
        try:
            self.sock.close()
        except:
            pass

def send_master(msg):
    global mhandler
    LOG.debug('send_master(%s)' % msg)
    try:
        mhandler.send(str(msg) + '\n')
        LOG.debug('send_master() completed')
    except AttributeError:
        LOG.debug('mhandler.send does not exist')
        LOG.debug('type(mhandler) = %s' % str(type(mhandler)))

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

    # Create the necessary classes.
    mhandler = MasterHandler(pid, address, port)
    handler = WorkerThread(address, root_port+pid, pid)
    leaders = [(root_port + i, 1) for i in xrange(N)]
    communicator = Communicator(incoming, incoming_lock, pid, send, mhandler)
    replica = Replica(leaders, '', communicator)

    # Spawn all threads.
    replica.start()
    mhandler.start()
    handler.start()

    LOG.debug('main() ends IDENTITY pid: %d, port: %d ' % (pid, port))

if __name__ == "__main__":
    main()

