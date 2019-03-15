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


def com_server(port):
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
                    print('%s: %s: %s ' % (
                        datetime.datetime.now().time(),
                        rsock.getpeername()[0],
                       data.decode('utf-8').strip()
                    ), end='')
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
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    print('Starting server on port %d...' % (port))
    com_server(port)
