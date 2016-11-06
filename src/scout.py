import logging as LOG
from threading import Thread, Lock

class Scout(Thread):
    def __init__(self, myleader, acceptors, b, communicator):
        Thread.__init__(self)
        self.acceptors = acceptors
        self.b = b
        self.myleader = myleader

        self.send = send, self.receive = communicator.build('scout')
        LOG.debug("Scout(): acceptors = %s" % str(acceptors))

    def run(self):
        LOG.debug('SCOUT running')
        waitfor = self.acceptors
        pvalues = []

        # send to all acceptors
        for acceptor in acceptors:
            send_msg = "p1a:" + str(b)
            self.send(acceptor, send_msg)

        while True:
            # sender = person that sent msg
            sender, msg = self.receive()
            LOG.debug("SCOUT: receive: " + str(msg) + " , SENDER: " + str(sender))
            msg = msg.split(":")

            # Case 1
            if msg[0] == "p1b":
                b = int(msg[1])
                bsp = ast.literal_eval(msg[2])
                if b == self.b:
                    pvalues = list(set(bsp).union(pvalues))
                    waitfor = waitfor - sender
                    if len(waitfor) < len(acceptors)/2:
                        send_msg = "adopted:" + str(self.b) + ":" + str(pvalues)
                        self.send(sender, send_msg)
                        break

                else:
                    send_msg = "preempted:" + str(b)
                    self.send(sender, send_msg)
                    break
