import logging as LOG
from threading import Thread, Lock

class Replica(Thread):
    def __init__(self, leaders, initial_state, send, receive):
        Thread.__init__(self)
        self.decisions = []
        self.leaders = leaders
        self.proposals = []
        self.state = initial_state
        self.slot_num = 1

        self.send = send
        self.receive = receive
        LOG.debug('Replica(): leaders = ' + str(leaders))

    def run(self):
        LOG.debug('replica.run() called')

