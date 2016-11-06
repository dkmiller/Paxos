import logging as LOG
from commander import Commander
from scout import Scout
from threading import Thread, Lock

class Leader(Thread):
    def __init__(self, acceptors, replicas, communicator):
        Thread.__init__(self)
        self.acceptors = acceptors
        self.communicator = communicator
        self.replicas = replicas

        self.send, self.receive = communicator.build('leader')
        LOG.debug('LEADER inited')

    def run(self):
        LOG.debug('LEADER running')
        ballot_num = 0
        active = False
        proposals = []
    
        # TODO
        me = self.communicator.identity('leader')
        scout = Scout(me, self.acceptors, ballot_num, self.communicator)
        scout.start()

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

                    # Spawn commander.
                    commander = Commander(self.acceptors, self.replicas, bsp, self.communicator)
                    commander.start()
                    #spawn Commander(self.acceptors, self.replicas, bsp)
               
            # Case 2
            if msg[0] == "adopted":
                pvalues = ast.literal_eval(msg[2])
                proposals = proposals (xor) pvalues
                for proposal in proposals:
                    bsp = (ballot_num, proposal[0], proposal[1])
                    commander = Commander(self.acceptors, self.replicas, bsp, self.communicator)
                    commander.start()
                    #Spawn Commander(self.acceptors, self.replicas, bsp)
                active = True
                
            # Case 3
            if msg[0] == "preempted":
                b = int(msg[1])
                if b > ballot_num:
                    active = False
                    ballot_num = b + 1
                    # TODO: Spawn Scout.
                    me = self.communicator.identity('leader')
                    scout = Scout(me, self.acceptors, ballot_num, self.communicator)
                    scout.start()
                    #spawn Scout(self.acceptors, ballot_num)
