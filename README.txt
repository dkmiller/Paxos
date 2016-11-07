Ashutosh Agarwal (ana63) and Daniel Miller (dm635).

Implementation of the Paxos protocol for CS 5414 at Cornell. No slip days were 
used for this project. To test our implementation on the various test cases 
found in tests, run 

python master.py < tests/<test name>.input &

Our implementation adheres as closely as possible to the description of Paxos 
given in Robbert van Renesse's paper "Paxos made moderately complex". Thus, 
there are classes for each of the following constructs:

Replica, Acceptor, Commander, Scout, Leader

In addition to these classes, the file server.py handles the actual sockets, 
the Communicator class provides a convenient "send / receive" abstraction, 
much like the pseudo-code in van Renesse's paper, and the Crash / CrashAfter 
classes abstract away the various "test case flags" in the assignment 
description. 

One tricky problem is: how to only spawn a Scout after all N processes are 
running. Our implementation assumes that a) all processes are running from the 
same folder, and b) they are started in increasing order, before any other 
commands. Under these assumptions, our approach is to only spawn a Scout after 
the process with "pid" N-1 has written its log file.

Logs for the various processes are created in the LOG folder, which should be 
ignored (along with its contents) while grading.

