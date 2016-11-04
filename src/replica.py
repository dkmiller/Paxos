import logging as LOG
from threading import Thread, Lock

class Replica(Thread):
    def __init__(self, leaders, initial_state, communicator):
        LOG.debug('Replica(): begin')
        Thread.__init__(self)
        self.decisions = []
        self.leaders = leaders
        self.proposals = []
        self.state = initial_state
        self.slot_num = 1

        LOG.debug('about to call build()')
        self.send, self.receive = communicator.build('replica')
        LOG.debug('Replica(): leaders = ' + str(leaders))

    def run(self):
        LOG.debug('replica.run() called')
        sender, msg = self.receive()
        LOG.debug('replica received')

