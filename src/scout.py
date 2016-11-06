import logging as LOG
from threading import Thread, Lock

class Scout(Thread):
    def __init__(self, myleader, acceptors, b, communicator):
        Thread.__init__(self)
        self.acceptors = acceptors
        self.b = b
        self.myleader = myleader

        self.send = send, self.receive = communicator.build('scout')
        LOG.debug('Scout(): acceptors = %s' % acceptors)

    def run(self):
        LOG.debug('Scout.run()')
        waitfor = list(self.acceptors) # Copy
        pvalues = []

        # send to all acceptors
        for acceptor in acceptors:
            send_msg = 'p1a:%s' % self.b
            self.send(acceptor, send_msg)

        while True:
            # sender = person that sent msg
            sender, msg = self.receive()
            LOG.debug('Scout.receive: (%s,%s)' % (sender, msg))
            msg = msg.split(':')

            if msg[0] == "p1b":
                b = int(msg[1])
                bsp = ast.literal_eval(msg[2])
                if b == self.b:
                    pvalues = list(set(bsp).union(pvalues))
                    waitfor = waitfor.remove(sender)
                    if 2*len(waitfor) < len(self.acceptors):
                        send_msg = 'adopted:%s:%s'% (self.b, pvalues)
                        self.send(self.myleader, send_msg)
                        break

                else:
                    send_msg = 'preempted:%s' % self.b
                    self.send(self.myleader, send_msg)
                    break
