import logging as LOG
from threading import Thread, Lock

class Replica(Thread):
    def __init__(self, leaders, initial_state, communicator):
        Thread.__init__(self)
        self.leaders = leaders
        self.state = initial_state

        self.send, self.receive = communicator.build('replica')
        LOG.debug('Replica(): leaders = ' + str(leaders))

    def run(self):
        LOG.debug('REPLICA running')
        slot_num = 1
        proposals = []
        decisions = []

        while True:
            sender, msg = self.receive()
            LOG.debug("REPLICA: receive: " + str(msg) + " , SENDER: " + str(sender))
            msg = msg.split(":")

            # Case 1
            if msg[0] == "request":
                p = int(msg[1])
                propose(p)


            
