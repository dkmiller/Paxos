#!/usr/bin/env python
"""
The master program for CS5414 three phase commit project.
"""

import sys, os
import subprocess
import time
from threading import Thread, Lock
from socket import SOCK_STREAM, socket, AF_INET

address = 'localhost'
threads = {}

msgs = {}

ack_lock = Lock()
acked_list = {}
wait_for_ack_list = {}
wait_for_ack = False
wait_chat_log = False

class ClientHandler(Thread):
    def __init__(self, index, address, port):
        Thread.__init__(self)
        self.index = index
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((address, port))
        self.buffer = ""
        self.valid = True

    def run(self):
        global threads, wait_chat_log, wait_for_ack
        while self.valid:
            if "\n" in self.buffer:
                (l, rest) = self.buffer.split("\n", 1)
                self.buffer = rest
                s = l.split()
                if len(s) < 2:
                    continue
                if s[0] == 'ack':
                    mid = int(s[1])
                    ack_lock.acquire()
                    acked_list[mid] = True
                    if mid in wait_for_ack_list:
                        del wait_for_ack_list[mid]
                    if len(wait_for_ack_list) == 0:
                        wait_for_ack = False
                    ack_lock.release()
                elif s[0] == 'chatLog':
                    chatLog = s[1]
                    print chatLog
                    wait_chat_log = False
                else:
                    print 'WRONG MESSAGE:', s
            else:
                try:
                    data = self.sock.recv(1024)
                    #sys.stderr.write(data)
                    self.buffer += data
                except:
                    print sys.exc_info()
                    self.valid = False
                    del threads[self.index]
                    self.sock.close()
                    break

    def send(self, s):
        if self.valid:
            self.sock.send(str(s) + '\n')

    def close(self):
        try:
            self.valid = False
            self.sock.close()
        except:
            pass

def send(index, data, set_wait=False):
    global threads, wait_chat_log
    while wait_chat_log:
        time.sleep(0.01)
    pid = int(index)
    if set_wait:
        wait_chat_log = True
    threads[pid].send(data)

def exit(exit=False):
    global threads, wait_chat_log

    wait = wait_chat_log
    wait = wait and (not exit)
    while wait:
        time.sleep(0.01)
        wait = wait_chat_log

    time.sleep(2)
    for k in threads:
        threads[k].close()
    subprocess.Popen(['./stopall'], stdout=open('/dev/null'), stderr=open('/dev/null'))
    time.sleep(0.1)
    os._exit(0)

def timeout():
    time.sleep(120)
    exit(True)

def main():
    global threads, wait_chat_log
    global wait_for_ack
    timeout_thread = Thread(target = timeout, args = ())
    timeout_thread.start()

    while True:
        line = ''
        try:
            line = sys.stdin.readline()
        except: # keyboard exception, such as Ctrl+C/D
            exit(True)
        if line == '': # end of a file
            exit()
        line = line.strip() # remove trailing '\n'
        if line == 'exit': # exit when reading 'exit' command
            while wait_for_ack:
                time.sleep(0.1)
            exit()
        sp1 = line.split(None, 1)
        sp2 = line.split()
        if len(sp1) != 2: # validate input
            continue
        pid = int(sp2[0]) # first field is pid
        cmd = sp2[1] # second field is command
        if cmd == 'waitForAck':
            mid = int(sp2[2])
            ack_lock.acquire()
            if mid not in acked_list:
                wait_for_ack = True
                wait_for_ack_list[mid] = True
            ack_lock.release()
        elif cmd == 'start':
            port = int(sp2[3])
            subprocess.Popen(['./process', str(pid), sp2[2], sp2[3]], stdout=open('/dev/null'), stderr=open('/dev/null'))
            # sleep for a while to allow the process be ready
            time.sleep(1)
            # connect to the port of the pid
            handler = ClientHandler(pid, address, port)
            threads[pid] = handler
            handler.start()
        else:
            wait = wait_for_ack
            while wait: # waitForAck wait_for_acks these commands
                time.sleep(2)
                wait = wait_for_ack
            if cmd == 'msg': # message msgid msg
                msgs[sp2[2]] = sp2[3]
                send(pid, sp1[1])
            elif cmd[:5] == 'crash': # crashXXX
                send(pid, sp1[1])
            elif cmd == 'get': # get chatLog
                while wait_chat_log: # get command blocks next get command
                    time.sleep(0.1)
                send(pid, sp1[1], set_wait=True)

if __name__ == '__main__':
    main()
