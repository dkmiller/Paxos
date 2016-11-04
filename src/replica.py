import logging as LOG
from threading import Thread, Lock

class Replica(Thread):
    def __init__(self, leaders, initial_state, communicator):
        Thread.__init__(self)
        self.decisions = []
        self.leaders = leaders
        self.proposals = []
        self.state = initial_state
        self.slot_num = 1

        self.send, self.receive = communicator.build('replica')
        LOG.debug('Replica(): leaders = ' + str(leaders))

    def run(self):
        while True:
            sender, msg = self.receive()
            LOG.debug('Replica.receive: (%s,\'%s\')' % (str(sender),msg))
            master = (-1, 'master')
            self.send(master, 'ack 0')
            LOG.debug('Replica.send: \'ack 0\'')

