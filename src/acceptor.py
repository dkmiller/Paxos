from threading import Thread, Lock
import ast
import logging as LOG

class Acceptor(Thread):
    def __init__(self, pid, N, send, receive):
        Thread.__init__(self)
        self.pid = pid
        self.N = N
        self.send = send
        self.receive = receive
        LOG.debug("ACCEPTOR inited")

    def run(self):
        LOG.debug("ACCEPTOR running")
        ballot_num = -1
        # List of <b,s,p>
        accepted = []

        while True:
            sender, msg = self.receive()
            LOG.debug("ACCEPTOR: receive: " + str(msg) + " , SENDER: " + str(sender))
            msg = msg.split(':')
            
            # Case 1
            if msg[0] == "p1a":
                b = int(msg[1])
                if b > ballot_num:
                    ballot_num = b
                send_msg = "p1b:" + str(ballot_num) + ":" + str(accepted)
                self.send(sender, send_msg)

            # Case 2
            elif msg[1] == "p2a":
                bsp = ast.literal_eval(msg[1])
                b = bsp[0]
                s = bsp[1]
                p = bsp[2]
                if b >= ballot_num:
                    ballot_num = b
                    accepted = list(set([bsp]).union(accepted))
                send_msg = "p2b:" + str(ballot_num)
                self.send(sender, send_msg)
