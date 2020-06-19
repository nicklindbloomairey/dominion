#!/usr/bin/env python3
import socket
import selectors
import sys

HEADER_LENGTH = 10

if len(sys.argv) != 4:
    print("usage:", sys.argv[0], "<host> <port> <username>")
    sys.exit(1)
HOST, PORT, USERNAME = sys.argv[1], int(sys.argv[2]), sys.argv[3]

sel = selectors.DefaultSelector()


sel.register(sys.stdin, selectors.EVENT_READ, data="stdin")

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send_wrapper(socket, msg):
    msg = msg.encode('utf-8')
    msg_header = f"{len(msg):<{HEADER_LENGTH}}".encode('utf-8')
    message = msg_header + msg
    totalsent = 0
    while totalsent < len(message):
        sent = socket.send(message[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent

socket.connect((HOST, PORT))
socket.setblocking(False)
#send_wrapper(socket, USERNAME)

try:
    while True:
        events = sel.select(timeout=1) #blocking
        for key, mask in events:
            if key.data == "stdin":
                message = sys.stdin.readline()
                #action, value = tuple(message.split())
                #socket.send(message) #send message from
                send_wrapper(message)
                continue
            else:
                print('else')
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()

