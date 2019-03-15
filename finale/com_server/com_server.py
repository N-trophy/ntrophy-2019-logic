#!/usr/bin/env python3

"""
N-trophy 2019 logic's final task:
Server for ESP32-Learning Kits communication

Input ports of server: 1000,1100
Input ports of ESPs: 2000,2100

Data flow: everything on port 2000
"""

import socket
import types
import select
import sys
import datetime

DEFAULT_PORT = 2000


def com_server(port, log_file):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen()

    connected = []

    while True:
        rsocks, wsocsk, esocks = select.select(
            [server_socket] + connected, [], []
        )

        for rsock in rsocks:
            if rsock == server_socket:
                # New connection
                sockfd, addr = rsock.accept()
                sockfd.setblocking(0)
                connected.append(sockfd)
                print('New connection: %s' % (str(addr)))
            else:
                try:
                    data = rsock.recv(1024)
                except socket.error:
                    data = None

                if data:
                    decoded = data.decode('utf-8').strip()
                    print('%s: %s: %s ' % (
                        datetime.datetime.now().time(),
                        rsock.getpeername()[0],
                        decoded
                    ), end='')
                    if decoded[0] == '0' or decoded[0] == '1':
                        log_file.write(decoded[0])
                        log_file.flush()

                    for s in filter(lambda s: s != rsock, connected):
                        print('-> %s' % (s.getpeername()[0]), end='')
                        try:
                            s.send(data)
                        except socket.error:
                            print('Error!', end='')
                    print()
                else:
                    print('Closing socket...')
                    connected.remove(rsock)
                    rsock.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('Usage: com_server.py filename port\n')
        sys.exit(1)
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    fn = sys.argv[1]
    print('Starting server on port %d, file %s...' % (port, fn))

    with open(fn, 'a') as f:
        f.write('\n'+str(datetime.datetime.now().time())+':\n')
        f.flush()
        com_server(port, f)
