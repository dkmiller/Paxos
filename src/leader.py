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
                LOG.debug("Leader: Inside propose")
                sp = ast.literal_eval(msg[1])
                s = sp[0]
                p = sp[1]
                if all([proposal[0] != s for proposal in proposals]):
                    # proposals = proposals union [sp]
                    if sp not in proposals:
                        proposals.append(sp)
                    if active:
                        bsp = (ballot_num, s, p)
                        LOG.debug("Leader spawning COM: " + str(bsp)) 
                        # Spawn commander.
                        Commander(self.acceptors, self.replicas, bsp, self.communicator).start()
               
            # Case 2
            if msg[0] == 'adopted':
                LOG.debug("--------------------ADOPTED-----------------")
                LOG.debug("PROPOSALS: " + str(proposals))
                pvalues = ast.literal_eval(msg[2])
                new_sp_list = self.pmax_op(pvalues)
                proposals = self.xor(proposals, new_sp_list)
                LOG.debug("After xor: " + str(proposals))
                for proposal in proposals:
                    bsp = (int(msg[1]), proposal[0], proposal[1])
                    LOG.debug("Leader spawning COM: " + str(bsp))
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
    
    def pmax_op(self, pvals):
        LOG.debug("PMAX: " + str(pvals))
        new_sp_list = []
        slots_done = []
        for bsp in pvals:
            b = bsp[0]
            s = bsp[1]
            p = bsp[2]
            if s in slots_done:
                continue
            for bsp2 in pvals:
                b2 = bsp2[0]
                s2 = bsp2[1]
                p2 = bsp2[2]
                if s == s2:
                    if b2 > b:
                        p = p2
            new_sp_list.append((s,p))
            slots_done.append(s)
        return new_sp_list
    
    def xor(self, x, y):
        new_sp_list = []
        slots_done = []
        for sp in y:
            new_sp_list.append(sp)
            slots_done.append(sp[0])
        for sp in x:
            if sp[0] not in slots_done:
                new_sp_list.append(sp)
        return new_sp_list
