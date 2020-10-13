#!/usr/bin/env python3
# CS472 - Homework #2
# Edward Parrish
# ftpclient.py
#
# This module is the major module of the FTP client, with the main processing loop.

from systemhelper import System
from mylogger import Logger
import socket

"""main()
The main processing loop of the FTP client. It initiates the TCP scoket and
begins the conersation for the FTP server.
"""


def main():
    # Get command line args
    host, filename, port = System.get_ftp_args()

    # Initialize client with log filename.
    client = Client(filename)

    # Test if port is None.
    if port is None:
        port = client.DEFAULT_CONNECT_PORT

    # Connect client to host no default port and receive data response.
    data = client.connect(host, port)

    # Test if server response indicates user credentials are needed.
    if (client.credentials_needed(data)):
        # Get user credentials from user.
        user, pswd = System.get_account_info(host, port)

        # Send credentials to server.
        data = client.login(user, pswd)

        # Test if login was unsuccessful.
        if (not client.login_successful(data)):
            # Display error and terminate processing.
            System.exit_('Server response: {0}'.format(data.decode()))
    else:
        System.exit_('Server response: {0}'.format(data.decode()))

    System.display('Login Successful.')
    System.display('Available Commands: ')

    # Display help menu.
    client.run_help()

    # The main processing loop.
    is_quit = False
    while not is_quit:
        # Get list user input args stripped of all whitespace.
        args = System.input_args()

        # Test arg length is greater than zero.
        if len(args) > 0:
            is_quit = client.run(args)


class Client:
    DEFAULT_CONNECT_PORT = 21
    DEFAULT_DATA_PORT = 20

    NEW_USER = 220
    LOGGED_IN = 230
    PASSWORD_NEEDED = 331
    # LOGIN_INCORRECT = 530

    QUIT = 'quit'
    HELP = 'help'
    LIST = 'ls'
    PWD = 'pwd'
    CWD = 'cd'
    GET = 'get'
    PUT = 'put'

    AVAIL_CMDS = [QUIT, HELP, LIST, PWD, CWD, GET, PUT]

    def __init__(self, filename):
        self.logger = Logger(filename)
        self.socket = socket.socket()
        self.host = None
        self.port = None

    #connect(host, port)
    def connect(self, host, port=DEFAULT_CONNECT_PORT):
        data = None

        try:
            # Connect to host on given port.
            self.socket.connect((host, port))
            self.logger.write_log(
                'Connecting to {0} on port {1}.'.format(host, port))

            # Receive connection confirmation.
            data = self.socket.recv(1024)
            self.logger.write_log('Received: {0}'.format(repr(data)))

            # Record current host and port.
            self.host = host
            self.port = port

        except TimeoutError as err:
            self.logger.write_log('A timeout error occurred: {0}'.format(err))
            System.exit_('A timeout error occurred: {0}'.format(err))

        return data

    def disconnect(self):
        discon_str = 'QUIT'

        # Send quit.
        self.socket.send((discon_str + '\r\n').encode())
        self.logger.write_log('Sent: {0}'.format(discon_str))

        # Receive server response.
        data = self.socket.recv(4096)
        self.logger.write_log('Received: {0}'.format(repr(data)))

    #login(user, pswd=None)
    def login(self, user, pswd=None):
        data = None
        user_str = 'USER {0}'.format(user)

        try:
            # Send username.
            self.socket.send((user_str + '\r\n').encode())
            self.logger.write_log('Sent: {0}'.format(user_str))

            # Receive username confirmation.
            data = self.socket.recv(4096)
            self.logger.write_log('Received: {0}'.format(repr(data)))

            # Test if reply code indicates password needed.
            if self.parse_reply_code(data) == self.PASSWORD_NEEDED:
                # Test if password is given.
                if pswd is not None:
                    pass_str = 'PASS {0}'.format(pswd)

                    # Send password.
                    self.socket.send((pass_str + '\r\n').encode())
                    self.logger.write_log('Sent: {0}'.format(pass_str))

                    # Receive password confirmation.
                    data = self.socket.recv(4096)
                    self.logger.write_log('Received: {0}'.format(repr(data)))

                else:
                    self.logger.write_log(
                        'A password is required for account.')
                    System.exit_('A password is required for account.')

        except Exception as err:
            self.logger.write_log('An error occurred: {0}'.format(err))
            System.exit_('An error occurred: {0}'.format(err))

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

            except Exception:
                self.logger.write_log('Server reply code unkown.')
                System.exit_('Server reply code unkown.')

        return result

    def run(self, args=[]):
        cmd = args[0]

        # Test if command is quit.
        if self.is_quit(cmd):
            is_quit = True
            self.disconnect()

        else:
            is_quit = False

            # Determine the user command and run.
            if self.is_help(cmd):
                self.run_help()

            if self.is_list(cmd):
                self.run_list(args)

            elif self.is_pwd(cmd):
                self.run_pwd(args)

            elif self.is_cwd(cmd):
                self.run_cwd(args)

            elif self.is_get(cmd):
                self.run_get(args)

            elif self.is_put(cmd):
                self.run_put(args)

        return is_quit

    def run_help(self):
        # Display the list of available commands.
        System.display('Some commands are abbreviated: ')
        System.display_list(self.AVAIL_CMDS)

    def run_port(self):
        port_str = 'PORT {0},0,20'.format(self.host.replace('.', ',')) 

        # Send PORT command.
        self.socket.send((port_str + '\r\n').encode())
        self.logger.write_log('Sent: ' + port_str)

        # Receive server response.
        data = self.socket.recv(4096)
        self.logger.write_log('Received: ' + repr(data))


    def run_list(self, args):
        dirs = ''
        if len(args) > 1:
            dirs = ' '.join(args[1:])

        list_str = 'LIST ' + dirs

        # Open data channel.
        self.run_port()
        
        # Send list command.
        self.socket.send((list_str + '\r\n').encode())
        self.logger.write_log('Sent: ' + list_str)

        # Receive server response.
        data = self.socket.recv(4096)
        self.logger.write_log('Received: ' + repr(data))

        return data
        

    def run_pwd(self, args):
        pwd_str = 'PWD'

        # Send PWD command.
        self.socket.send((pwd_str + '\r\n').encode())
        self.logger.write_log('Sent: ' + pwd_str)

        # Receive server response.
        data = self.socket.recv(4096)
        self.logger.write_log('Received: ' + repr(data))

        return data

    def run_cwd(self, args):
        #
        return False

    def run_get(self, args):
        #
        return False

    def run_put(self, args):
        #
        return False

    def is_quit(self, cmd):
        return cmd.lower() == self.QUIT.lower()

    def is_help(self, cmd):
        return cmd.lower() == self.HELP.lower()

    def is_list(self, cmd):
        return cmd.lower() == self.LIST.lower()

    def is_pwd(self, cmd):
        return cmd.lower() == self.PWD.lower()

    def is_cwd(self, cmd):
        return cmd.lower() == self.CWD.lower()

    def is_get(self, cmd):
        return cmd.lower() == self.GET.lower()

    def is_put(self, cmd):
        return cmd.lower() == self.PUT.lower()

    def credentials_needed(self, data):
        return self.parse_reply_code(data) == self.NEW_USER

    def login_successful(self, data):
        return self.parse_reply_code(data) == self.LOGGED_IN


if __name__ == '__main__':
    main()
