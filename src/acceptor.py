from threading import Thread, Lock

class Acceptor(Thread):
    def __init__(self, pid, N):
        self.pid = pid
        self.N = N

    def run(self):
        filename = str(self.pid) + '.log'
        with open(filename, 'a+') as f:
            f.write('run Acceptor')

        # TODO: while True:
