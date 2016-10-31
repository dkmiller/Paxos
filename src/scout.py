from threading import Thread, Lock

class Scout(Thread):
    def __init__(self, acceptors, b, leader):
        this.acceptors = acceptors
        this.b = b
        this.leader = leader
        this.pvalues = []
        this.waitfor = list(acceptors)

    def run(self):
        filename = str(self.pid) + '.log'
        with open(filename, 'a+') as f:
            f.write('run Scout')
