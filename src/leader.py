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
        spawn scout

        while True:
            sender, msg = self.receive()
            LOG.debug("LEADER: receive: " + str(msg) + " , SENDER: " + str(sender))
            msg = msg.split(":")
            sp = ast.literal_eval(msg[1])
            s = int(sp[0])
            p = int(sp[1])
            
            # Case 1
            if msg[0] == "propose":
                proposals = list(set([sp]).union(proposals))
                if active:
                    # TODO
                    spawn Commander


                
