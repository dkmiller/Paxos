import logging as LOG
import os
from Queue import Queue
from replica import Replica
import sys
from threading import Lock

incoming = {}
master_thread = None
N = None
pid = None
port = None
receive_threads = {}
send_thread = None

def new_instance(kind):
    global incoming, pid
    subid = None
    if kind == 'acceptor':
        subid = 0
    elif kind == 'commander':
        if len(incoming) > 0:
            subid = max(3, max(incoming.keys())) + 1
        else:
            subid = 4
    elif kind == 'leader':
        subid = 1
    elif kind == 'replica':
        subid = 2
    elif kind == 'scout':
        subid = 3
    incoming[subid] = Queue()
    def receive():
        m = incoming[subid].get(block=True).split(':',2)
        sender_port = int(m[0])
        sender_subid = int(m[1])
        msg = m[2]
        LOG.debug('received: ' + msg)
        return ((sender_port, sender_subid), msg)
    def send(recipient, msg):
        recipient_port, recipient_subid = sender_port
        header = '%d:%d:%d:%d:' % (20000+pid, subid, recipient_port, recipient_subid)
        msg_to_send = header + msg
        LOG.debug('send: ' + msg_to_send)
    return (send, receive)

def main():
    global N, pid, port

    # Read global state.
    pid = int(sys.argv[1])
    N = int(sys.argv[2])
    port = int(sys.argv[3])

    LOG.basicConfig(filename=str(pid) + '.log', level=LOG.DEBUG)
    LOG.debug('pid: %d' % pid)

    # Spawn the necessary threads.

    # Create the replica running on this process.
    leaders = [(20000+i, 1) for i in xrange(N)]
    send, receive = new_instance('replica')

    # Spawn the replica.
    replica = Replica(leaders, '', send, receive)
    replica.start()

    LOG.debug('main ends')

if __name__ == "__main__":
    main()

