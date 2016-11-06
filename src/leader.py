import ast
import logging as LOG
from threading import Thread, Lock

from commander import Commander
from scout import Scout

class Leader(Thread):
    def __init__(self, acceptors, replicas, communicator):
        Thread.__init__(self)
        self.acceptors = acceptors
        self.communicator = communicator
        self.replicas = replicas

        self.send, self.receive = communicator.build('leader')
        LOG.debug('Leader()')

    def run(self):
        LOG.debug('Leader.run()')
        ballot_num = 0
        active = False
        proposals = []
    
        # Spawn a scout.
        me = self.communicator.identity('leader')
        Scout(me, self.acceptors, ballot_num, self.communicator).start()

        while True:
            sender, msg = self.receive()
            LOG.debug('Leader.receive: (%s,%s)' % (sender, msg))
            msg = msg.split(':')
            
            # Case 1
            if msg[0] == 'propose':
                sp = ast.literal_eval(msg[1])
                s = int(sp[0])
                p = int(sp[1])
                # proposals = proposals union [sp]
                if sp not in proposals:
                    proposals.append(sp)
                if active:
                    bsp = (ballot_num, s, p)

                    # Spawn commander.
                    Commander(self.acceptors, self.replicas, bsp, self.communicator).start()
               
            # Case 2
            if msg[0] == 'adopted':
                pvalues = ast.literal_eval(msg[2])
                proposals = self.xor(proposals, self.pmax(pvalues))
                for proposal in proposals:
                    bsp = (ballot_num, proposal[0], proposal[1])
                    Commander(self.acceptors, self.replicas, bsp, self.communicator).start()
                active = True
                
            # Case 3
            if msg[0] == "preempted":
                b = int(msg[1])
                if b > ballot_num:
                    active = False
                    ballot_num = b + 1
                    # Spawn Scout.
                    me = self.communicator.identity('leader')
                    Scout(me, self.acceptors, ballot_num, self.communicator).start()
    def pmax(self, pvals):
        pass
    def xor(x, y):
        pass
