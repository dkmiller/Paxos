import logging as LOG

class Scout(Thread):
    def __init__(self, myleader, acceptors, b, send, receive):
        Thread.__init__(self)
        self.acceptors = acceptors
        self.b = b
        self.myleader = myleader
        self.send = send
        self.receive = receive
        LOG.debug("SCOUT inited")

    def run(self):
        LOG.debug('SCOUT running')
        waitfor = self.acceptors
        pvalues = []

        # send to all acceptors
        for acceptor in acceptors:
            send_msg = "p1a:" + str(b)
            # TODO:
            this.send(acceptor, send)
            
