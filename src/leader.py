import logging as LOG
from threading import Thread, Lock

class Leader(Thread):
    def __init__(self, acceptors, replicas, send, receive):
        self.acceptors = acceptors
        self.active = False
        self.ballot_num = 0
        self.proposals = []
        self.replicas = replicas

        self.send = send
        self.receive = receive
        LOG.debug('Leader() called')

    def run(self):
        LOG.debug('thread.run() called')
        while True:
            sender, msg = self.receive()
            LOG.debug('msg = ' + msg)
