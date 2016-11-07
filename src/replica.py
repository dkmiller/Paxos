import ast
import inspect
import logging as LOG
from threading import Thread, Lock

class Replica(Thread):
    def __init__(self, leaders, initial_state, communicator):
        Thread.__init__(self)
        self.leaders = leaders
        self.state = initial_state
        self.message_to_log = ''

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

            # Case 1: request
            if sender[1] == 'master':
                LOG.debug('Replica.receive: received from master')
                msg = msg.split()
                
                if msg[0] == "msg":
                    p = int(msg[1]) # Message ID
                    self.message_to_log = msg[2]
                    self.propose(p)
                    LOG.debug('Replica.receive: propose() done')
                    continue
                if msg[0] == "get":
                    masterid = (-1,'master')
                    send_msg = "chatLog "
                    for my_s in self.state:
                        send_msg += str(my_s) + "-" + str(self.state[my_s]) + ","
                    self.send(masterid, send_msg[:-1])
                    continue

            msg = msg.split(':')

#            if msg[0] == "give_internal_state":
#                LOG.debug("REPLICA: GIVING INTERNAL STATE")
#                send_msg = "internal_state:" + str(self.decisions)
#                self.send(sender, send_msg)

            # Case 2
            if msg[0] == "decision":
                LOG.debug('Replica: DECISION-------------------------')
                sp = ast.literal_eval(msg[1])
                #new_list = ast.literal_eval(msg[2])
                LOG.debug('Replica: DECISION sp = ' + str(sp))

                ##self.decisions = list(set(new_list).union(self.decisions))
                # decisions = decisions union [sp]
                if sp not in self.decisions:
                    self.decisions.append(sp)

##                masterid = (-1,'master')
##                self.send(masterid, "ack " + str(sp[1]) + " " + str(sp[0]))

                while any([decision[0] == self.slot_num for decision in self.decisions]):
                    for decision in self.decisions:
                        if self.slot_num == decision[0]:
                            p_dash = decision[1]
                            proposed = False

                            for proposal in self.proposals:
                                p_ddash = proposal[1]
                                if self.slot_num == proposal[0]:
                                    if p_dash != p_ddash:
                                        self.propose(p_ddash)
                                        proposed = True
                                        break

                            if not proposed:
                                self.perform(p_dash)

    def propose(self, p):
        LOG.debug('Replica.propose: p=%s' % p)
        if all([decision[1] != p for decision in self.decisions]):
            new_list = list(set(self.proposals).union(self.decisions))
            s_dash = 1
            while any([val[0] == s_dash for val in new_list]):
                s_dash += 1
            sp = (s_dash, p)
            self.proposals = list(set([sp]).union(self.proposals))
            for leader in self.leaders:
                send_msg = 'propose:' + str(sp)
                self.send(leader, send_msg)

    def perform(self, p):
        incremented = False
        for s in range(1,self.slot_num):
            if (s,p) in self.decisions:
                self.slot_num += 1
                incremented = True
                break
        
        if not incremented:
            self.state[self.slot_num] = p
            LOG.debug("----------------ANSWER: " + str(self.slot_num) + ", " + str(p))
            masterid = (-1,'master')
            self.send(masterid, 'ack ' + str(p) + ' ' + str(self.slot_num))
            self.slot_num += 1
