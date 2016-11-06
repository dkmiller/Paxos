import logging as LOG
from threading import Thread, Lock

class Leader(Thread):
    def __init__(self, acceptors, replicas, send, receive):
        Thread.__init__(self)
        self.acceptors = acceptors
        self.replicas = replicas
        self.send = send
        self.receive = receive
        LOG.debug('LEADER inited')

    def run(self):
        LOG.debug('LEADER running')
        ballot_num = 0
        active = False
        proposals = []
    
        # TODO
        spawn scout(self.acceptors, ballot_num)

        while True:
            sender, msg = self.receive()
            LOG.debug("LEADER: receive: " + str(msg) + " , SENDER: " + str(sender))
            msg = msg.split(":")
            
            # Case 1
            if msg[0] == "propose":
                sp = ast.literal_eval(msg[1])
                s = int(sp[0])
                p = int(sp[1])
                proposals = list(set([sp]).union(proposals))
                if active:
                    bsp = (ballot_num, s, p)
                    # TODO
                    spawn Commander(self.acceptors, self.replicas, bsp)
               
            # Case 2
            if msg[0] == "adopted":
                pvalues = ast.literal_eval(msg[2])
                proposals = proposals (xor) pvalues
                for proposal in proposals:
                    bsp = (ballot_num, proposal[0], proposal[1])
                    # TODO:
                    Spawn Commander(self.acceptors, self.replicas, bsp)
                active = True
                
            # Case 3
            if msg[0] == "preempted":
                b = int(msg[1])
                if b > ballot_num:
                    active = False
                    ballot_num = b + 1
                    # TODO:
                    spawn Scout(self.acceptors, ballot_num)
