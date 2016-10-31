import logging as LOG
import os
from Queue import Queue
from replica import Replica
import sys
from threading import Lock

incoming = {}
N = None
pid = None
port = None

def new_instance(kind):
    return (None, None)

def main():
    global N, pid, port
    pid = int(sys.argv[1]) # This server's id, from 0..N-1
    N = int(sys.argv[2]) # Total number of servers.
    port = int(sys.argv[3]) # Port number the server should listen on.

    LOG.basicConfig(filename=str(pid) + '.log', level=LOG.DEBUG)
    LOG.debug('pid: %d' % pid)

    send, receive = new_instance('replica')
    leaders = []
    for i in xrange(N):
        leader_port = 20000 + i
        leader_subid = 1
        leaders.append((leader_port, leader_subid))

    replica = Replica(leaders, '', send, receive)
    replica.start()

    LOG.debug('Replica()')

if __name__ == "__main__":
    main()
