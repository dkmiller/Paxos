import logging as LOG

class Replica:
    def __init__(self, decisions, leaders, pid, receive, send, subnet)
        self.decisions = decisions
        self.leaders = leaders
        self.pid = pid
        self.proposals = []
        LOG.debug('Replica(%d) called' % pid)

    def run(self):
        LOG.debug('replica.run() called')
        while True:
            pass
            for leader in leaders:
                send(leader, msg)
