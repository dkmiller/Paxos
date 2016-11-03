from threading import Thread, Lock

class Acceptor(Thread):
    def __init__(self, pid, N):
        self.pid = pid
        self.N = N

    def run(self):
        ballot_num = None, accepted = []

        # TODO: while True:
