import logging as LOG
from threading import Lock

def die():
    import os
    LOG.debug('CRASHING *********************')
    os._exit()

class Crash:
    def __init__(self):
        die()

class CrashAfter:
    def __init__(self, word, pids):
        self.lock = Lock()
        self.pids = pids
        self.word = word
    def should_I_die(self, msg):
        if self.word in msg:
            sender_pid = int(msg.split(':')[0])
            with self.lock:
                if sender_pid in self.pids: self.pids.remove(sender_pid)
            if len(self.pids) == 0:
                die()
