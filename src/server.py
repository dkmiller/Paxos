import logging as LOG
import os
import sys

from replica import Replica

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
