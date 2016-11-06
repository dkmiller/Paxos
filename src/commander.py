import logging as LOG
from threading import Thread, Lock

class Commander(Thread):
    def __init__(self, acceptors, replicas, bsp, communicator):
        Thread.__init__(self)
        self.acceptors = acceptors
        self.replicas = replicas
        self.bsp = bsp

        self.send, self.receive = communicator.build('commander')
        LOG.debug('Commander()')

    def run(self):
        LOG.debug('Commander.run()')
	waitfor = list(self.acceptors) # Copy of self.acceptors.

        # send to all acceptors
        for acceptor in self.acceptors:
            send_msg = 'p2a:%s' % self.bsp
            self.send(acceptor, send_msg)

        while True:
            sender, msg = self.receive()
            LOG.debug('Commander.receive: %s, sender: %s' % (msg, sender))
            msg = msg.split(':')

            # Case 1
            if msg[0] == 'p2b':
                b = int(msg[1])
                if b == self.b:
                    waitfor.remove(sender)
                    if 2*len(waitfor) < len(self.acceptors):
                        for replica in self.replicas:
                            sp = (self.bsp[1], self.bsp[2])
                            send_msg = 'decision:%s' % sp
                            self.send(replica, send_msg)
                        break

                else:
                    send_msg = 'preempted:%s' % b
                    self.send(sender, send_msg)
                    LOG.debug('Commander.run: %s' % send_msg)
                    break # This will exit the while loop, ending the thread.
