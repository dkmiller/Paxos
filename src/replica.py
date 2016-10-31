import os
import logging
import sys

class Replica:
    def __init__(self, pid):
        logging.debug('replica %d called' % pid)

