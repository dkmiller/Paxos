import ast
import logging as LOG
from threading import Thread, Lock

class Acceptor(Thread):
    def __init__(self, communicator):
        Thread.__init__(self)
        self.send, self.receive = communicator.build('acceptor')
        LOG.debug('Acceptor()')

    def run(self):
        LOG.debug("ACCEPTOR running")
        ballot_num = (-1,-1)
        # List of <b,s,p>
        accepted = []

        while True:
            sender, msg = self.receive()
            LOG.debug("ACCEPTOR: receive: %s, SENDER: %s" % (msg, str(sender)))
            msg = msg.split(':')
            
            # Case 1
            if msg[0] == "p1a":
                b = ast.literal_eval(msg[1])
                if b > ballot_num:
                    ballot_num = b
                send_msg = "p1b:" + str(ballot_num) + ":" + str(accepted)
                LOG.debug("ACCEPTOR sending msg to scout")
                self.send(sender, send_msg)

            # Case 2
            elif msg[0] == "p2a":
                bsp = ast.literal_eval(msg[1])
                b = bsp[0]
                s = bsp[1]
                p = bsp[2]
                LOG.debug('Acceptor.run(): (b, s, p) = (%s,%s,%s)' % (str(b),str(s),str(p)))
                if b >= ballot_num:
                    ballot_num = b
                    accepted = list(set([bsp]).union(accepted))
                send_msg = "p2b:" + str(ballot_num)
                self.send(sender, send_msg)
