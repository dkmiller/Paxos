import logging as LOG

class Scout:
    def __init__(self, acceptors, b, leader):
        this.acceptors = acceptors
        this.b = b
        this.leader = leader
        this.pvalues = []
        this.waitfor = list(acceptors)

    def run(self):
        LOG.debug('scout.run() called')
