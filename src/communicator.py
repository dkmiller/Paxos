from Queue import Queue
import logging as LOG

# A send/receive factory. Constructs, for any kind of thread
# (e.g. replica, leader, etc.) send and receive functions.
class Communicator:
    def __init__(self, incoming, incoming_lock, pid, send, mhandler):
        self.commander_seq = 0
        self.incoming = incoming
        self.incoming_lock = incoming_lock
        self.mhandler = mhandler
        self.pid = pid
        self.send = send

    # Returns an "identity" (pid, kind) for the calling thread.
    def identity(self, kind):
        LOG.debug("COMMUNICATOR: " + str(self.pid))
        return (self.pid, kind)

    # Returns (send, receive) functions (as a pair) for the calling thread.
    def build(self, kind):
        with self.incoming_lock:
            if kind == 'commander':
                subid = self.commander_seq
                commander_seq += 1
            else:
                subid = kind
            if subid not in self.incoming:
                self.incoming[subid] = Queue()
            # WARNING: if this is not the first scout, there still may be 
            # messages from the old scout on the queue.

        # Syntax: sender, message = receive().
        def my_receive():
            # Blocks until a message is ready.
            LOG.debug('Communicator.receive: before block')
            content = self.incoming[subid].get(block=True)
            LOG.debug('Communicator.receive: after block')
            content = content.split(':',4)
            sender = (int(content[0]),content[1]) # (pid, subid)
            # Skip recipient pid, subid.
            message = content[4]
            return (sender, message)

        def my_send(recipient, message):
            LOG.debug('Communicator.send')
            recipient_pid, recipient_subid = recipient
            if recipient_subid == 'master':
                self.mhandler.send(message)
            else:
                header = '%d:%s:%d:%s:' % (self.pid, str(subid), recipient_pid, recipient_subid)
                send_message = header + message
                self.send(recipient_pid, send_message)

        return (my_send, my_receive)

