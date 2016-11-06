import logging as LOG
from threading import Thread, Lock

class Replica(Thread):
    def __init__(self, leaders, initial_state, communicator):
        Thread.__init__(self)
        self.leaders = leaders
        self.state = initial_state

        self.send, self.receive = communicator.build('replica')
        
        self.slot_num = 1
        self.proposals = []
        self.decisions = []
        
        LOG.debug('Replica(): leaders = %s' % leaders)

    def run(self):
        LOG.debug('Replica.run()')

        while True:
            sender, msg = self.receive()
            LOG.debug('Replica.receive: (%s,%s)' % (sender, msg))
            self.message_to_log = ''

            # Case 1: request
            if sender[1] == 'master':
               msg = msg.split()
               p = int(msg[1]) # Message ID
               self.message_to_log = msg[2]
               propose(p)

            msg = msg.split(':')
            # Case 2
            if msg[0] == "decision":
                sp = ast.literal_eval(msg[1])
                # decisions = decisions union [sp]
                if sp not in self.decisions:
                    self.decisions.append(sp)

                for decision in self.decisions:
                    p_dash = decision[1]
                    if self.slot_num == decision[0]:
                        proposed = False

                        for proposal in self.proposals:
                            p_ddash = proposal[1]
                            if self.slot_num == proposal[0]:
                                if p_dash != p_ddash:
                                    propose(p_ddash)
                                    proposed = True

                        if not proposed:
                            perform(p_dash)

    def propose(p):
        if all([decision[1] != p for decision in self.decisions]):
            new_list = list(set(self.proposals).union(self.decisions))
            s_dash = 1
            while any([val[0] == s_dash for val in new_list]):
                s_dash += 1
            sp = (s_dash, p)
            self.proposals = list(set([sp]).union(self.proposals))
            for leader in self.leaders:
                send_msg = "propose:" + str(sp)
                self.sender(leader, send_msg)

    def perform(p):
        incremented = False
        for s in range(1,self.slot_num):
            if (s,p) in self.decisions:
                self.slot_num += 1
                incremented = True
                break
        
        if not incremented:
            self.state += ',%s' % self.message_to_log
            self.slot_num += 1
            masterid = (-1,'master')
            self.send(masterid, 'ack %d' % p)
