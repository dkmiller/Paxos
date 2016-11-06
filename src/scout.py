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

        while True:
            sender, msg = self.receive() # Wrong - receive from acceptor
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
                        send_msg = "adopted:" + str(self.b) + str(pvalues)
                        self.send(sender, send_msg)
                        break

                else:
                    send_msg = "preempted:" + str(b)
                    self.send(sender, send_msg)
                    break
