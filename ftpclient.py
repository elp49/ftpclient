#!/usr/bin/env python3
# CS472 - Homework #2
# Edward Parrish
# ftpclient.py
#
# This module is the major module of the FTP client, with the main processing loop.

from systemhelper import get_ftp_args, exit_
from mylogger import Logger
# from mysocket import Socket
import socket

"""main()
The main processing loop of the FTP client. It initiates the TCP scoket and
begins the conersation for the FTP server.
"""


def main():
    USERNAME = 'cs472'
    PASSWORD = 'hw2ftp'

    # Get command line args
    host, filename, port = get_ftp_args()
    
    # Initialize client with log filename.
    client = Client(filename)

    # Connect client to host no given port and receive response.
    data = client.connect(host, port)

    # Test if user credentials are needed.
    if (client.parse_reply_code(data) == client.NEW_USER):
        # Send credentials to server.
        data = client.login(USERNAME, PASSWORD)


class Client:
    NEW_USER = 220
    LOGGED_IN = 230
    PASSWORD_NEEDED = 331

    def __init__(self, filename):
        self.logger = Logger(filename)
        self.socket = socket.socket()

    #connect(host, port)
    def connect(self, host, port):
        data = None

        try:
            # Connect to host on given port.
            self.socket.connect((host, port))
            self.logger.write_log('Connecting to {0} on port {1}.'.format(host, port))

            # Receive connection confirmation.
            data = self.socket.recv(1024)
            self.logger.write_log('Received: {0}.'.format(repr(data)))

        except TimeoutError as err:
            self.logger.write_log('A timeout error occurred: {0}'.format(err))
            exit_('A timeout error occurred: {0}'.format(err))

        return data

    #login(user, pswd=None)
    def login(self, user, pswd=None):
        data = None
        user_str = 'USER {0}'.format(user)
        
        try:
            # Send username.
            self.socket.send((user_str + '\r\n').encode())
            self.logger.write_log('Sent: ' + user_str + '.')

            # Receive username confirmation.
            data = self.socket.recv(4096)
            self.logger.write_log('Received: {0}.'.format(repr(data)))

            # Test if reply code indicates password needed.
            if self.parse_reply_code(data) == self.PASSWORD_NEEDED:
                # Test if password is given.
                if pswd is not None:
                    pass_str = 'PASS {0}'.format(pswd)

                    # Send password.
                    self.socket.send((pass_str + '\r\n').encode())
                    self.logger.write_log('Sent: ' + pass_str + '.')

                    # Receive password confirmation.
                    data = self.socket.recv(4096)
                    self.logger.write_log('Received: {0}.'.format(repr(data)))

                else:
                    self.logger.write_log('A password is required for account.')
                    exit_('A password is required for account.')

        except Exception as err:
            self.logger.write_log('An error occurred: {0}'.format(err))
            exit_('An error occurred: {0}'.format(err))

        return data

    def parse_reply_code(self, data):
        result = None

        if data is not None:
            # Test data type.
            if isinstance(data, bytes):
                data_str = data.decode().split(' ')[0]

            elif isinstance(data, str) and len(data) > 0:
                data_str = data.split(' ')[0]

            try:
                # Cast code to int.
                result = int(data_str)
                
            except Exception as err:
                self.logger.write_log('Server reply code unkown.')
                exit_('Server reply code unkown.')


        return result


if __name__ == '__main__':
    main()
