from threading import Thread, Lock

class Leader(Thread):
    def __init__(self, acceptors, N, pid, replicas):
        self.acceptors = acceptors
        self.active = False
        self.ballot_num = 0
        self.N = N
        self.pid = pid
        self.proposals = []
        self.replicas = replicas

    def run(self):
        filename = str(self.pid) + '.log'
        with open(filename, 'a+') as f:
            f.write('run Leader')
        # TODO: while True:
