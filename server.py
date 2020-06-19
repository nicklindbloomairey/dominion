#!/usr/bin/env python3
import socket
import selectors
import sys

HEADER_LENGTH = 10

if len(sys.argv) != 3:
    print("usage:", sys.argv[0], "<host> <port>")
    sys.exit(1)
HOST, PORT = sys.argv[1], int(sys.argv[2])

clients = []
sel = selectors.DefaultSelector()

def accept_wrapper(sock):
    global num_connections
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from", addr)
    conn.setblocking(False)
    clients.append(conn)
    sel.register(conn, selectors.EVENT_READ)
    return

def myreceive(sock, msglen):
        chunks = []
        bytes_recd = 0
        while bytes_recd < msglen:
            chunk = sock.recv(min(msglen - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print('echoing', repr(data.outb), 'to', data.addr)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Avoid bind() exception: OSError: [Errno 48] Address already in use
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((HOST, PORT))
lsock.listen()
print("listening on", (HOST, PORT))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data='listen')

try:
    while True:
        #print("number of open connections:",num_connections)
        events = sel.select(timeout=None) #blocking
        for key, mask in events:
            if key.data == 'listen': #new connection
                accept_wrapper(key.fileobj)
            else:
                print(receive_message(key.fileobj))
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()


