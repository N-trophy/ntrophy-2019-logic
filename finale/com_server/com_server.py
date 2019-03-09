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


LISTEN_PORTS = (2000,)


def main():
    server_sockets = []
    for port in LISTEN_PORTS:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', port))
        s.listen()
        server_sockets.append(s)

    connected = []

    while True:
        rsocks, wsocsk, esocks = select.select(server_sockets + connected, [], [])

        for rsock in rsocks:
            if rsock in server_sockets:
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
                    print('%s: %s ' % (
                        str(rsock.getpeername()), data.decode('utf-8').strip()
                    ), end='')
                    for s in filter(lambda s: s != rsock, connected):
                        print('-> %s' % (str(s.getpeername())), end='')
                        try:
                            s.send(data)
                        except socket.error:
                            print('Error!', end='')
                    print()
                else:
                    #print('Closing socket %s...' % (str(rsock.getpeername() if rsock.)))
                    print('Closing socket...')
                    connected.remove(rsock)
                    rsock.close()


if __name__ == '__main__':
    main()
