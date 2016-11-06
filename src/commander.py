from threading import Thread, Lock
import logging as LOG

class Commander(Thread):
    def __init__(self, acceptors, replicas, bsp, send, receive):
        Thread.__init__(self)
        self.acceptors = acceptors
        self.replicas = replicas
        self.bsp = bsp
        self.send = send
        self.receive = receive
        LOG.debug("COMMANDER inited")

    def run(self):
        LOG.debug('COMMANDER running')
	waitfor = self.acceptors
        pvalues = []

        # send to all acceptors
        for acceptor in acceptors:
            send_msg = "p2a:" + str(self.bsp)
            # TODO:
            self.send(acceptor, send_msg)

        while True:
            sender, msg = self.receive() # Wrong - receive from acceptor
            LOG.debug("COMMANDER: receive: " + str(msg) + " , SENDER: " + str(sender))
            msg = msg.split(":")

            # Case 1
            if msg[0] == "p2b":
                b = int(msg[1])
                if b == self.b:
                    pvalues = list(set(self.bsp).union(pvalues))
                    waitfor = waitfor - sender
                    if len(waitfor) < len(self.acceptors)/2:
                        for replica in self.replicas:
                            sp = (self.bsp[1], self.bsp[2])
                            send_msg = "decision:" +str(sp))
                            self.send(replica, send_msg)
                        break

                else:
                    send_msg = "preempted:" + str(b)
                    self.send(sender, send_msg)
                    break
