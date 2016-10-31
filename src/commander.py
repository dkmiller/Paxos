from threading import Thread, Lock

class Commander(Thread):
    def __init__(self, acceptors, b, leader, N, p, pid, replicas, s):
        self.acceptors = acceptors
        self.b = b
        self.leader = leader
        self.N = N
        self.p = p
        self.pid = pid
        self.replicas = replicas
        self.s = s
        self.waitfor = list(acceptors)

    def run(self):
        filename = str(self.pid)
        with open(filename, 'a+') as f:
            f.write('run Commander')
