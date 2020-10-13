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
    res = client.connect(host, port)

    # Test if server response indicates user credentials are needed.
    if (client.credentials_needed(res)):
        # Get user credentials from user.
        user, pswd = System.get_account_info(host, port)

        # Send credentials to server.
        res = client.login(user, pswd)

        # Test if login was unsuccessful.
        if (not client.login_successful(res)):
            # Display error and terminate processing.
            System.exit_('Server response: {0}'.format(res.decode()))
    else:
        System.exit_('Server response: {0}'.format(res.decode()))

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
    DATA_P1 = 154
    DATA_P2 = 185

    NEW_USER = 220
    LOGGED_IN = 230
    PATHN_CREATED = 257
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
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_sock = None

    #connect(host, port)
    def connect(self, host, port=DEFAULT_CONNECT_PORT):
        res = None

        try:
            # Connect to host on given port.
            self.socket.connect((host, port))
            self.logger.write_log(
                'Connecting to {0} on port {1}.'.format(host, port))

            # Get server response.
            res = self.get_server_response()
            self.log_res_received(res)

        except TimeoutError as err:
            self.logger.write_log('A timeout error occurred: {0}'.format(err))
            System.exit_('A timeout error occurred: {0}'.format(err))

        return res

    def disconnect(self):
        discon_str = 'QUIT'

        # Send quit.
        self.socket.send((discon_str + '\r\n').encode())
        self.log_msg_sent(discon_str)

        # Get server response.
        res = self.get_server_response()
        self.log_res_received(res)

    #login(user, pswd=None)
    def login(self, user, pswd=None):
        res = None
        user_str = 'USER {0}'.format(user)

        try:
            # Send username.
            self.socket.send((user_str + '\r\n').encode())
            self.log_msg_sent(user_str)

            # Get server response.
            res = self.get_server_response()
            self.log_res_received(res)

            # Test if reply code indicates password needed.
            if self.parse_reply_code(res) == self.PASSWORD_NEEDED:
                # Test if password is given.
                if pswd is not None:
                    pass_str = 'PASS {0}'.format(pswd)

                    # Send password.
                    self.socket.send((pass_str + '\r\n').encode())
                    self.log_msg_sent(pass_str)

                    # Get server response.
                    res = self.get_server_response()
                    self.log_res_received(res)

                else:
                    self.logger.write_log(
                        'A password is required for account.')
                    System.exit_('A password is required for account.')

        except Exception as err:
            self.logger.write_log('An error occurred: {0}'.format(err))
            System.exit_('An error occurred: {0}'.format(err))

        return res

    def parse_reply_code(self, res):
        result = None

        if res is not None:
            # Test response data type.
            if isinstance(res, bytes):
                res_str = res.decode().split(' ')[0]

            elif isinstance(res, str) and len(res) > 0:
                res_str = res.split(' ')[0]

            try:
                # Cast code to int.
                result = int(res_str)

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

    # def open_data_chan(self):
    #     self.data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     host_name = socket.gethostname()
    #     host_addr = socket.gethostbyname(host_name)
    #     self.data_sock.bind((host_addr, (self.DATA_P1*256) + self.DATA_P2))
    #     self.data_sock.listen(1)

    def open_data_chan(self, pasv_res):
        # Parse host and port.
        host_addr, p1, p2 = self.parse_host_and_port(pasv_res)
        print('host_addr: ' + host_addr)

        self.data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_sock.connect((host_addr, (p1*256) + p2))

    def parse_host_and_port(self, res):
        # Decode response.
        res_str = res.decode()

        # Get indices of left and right parentheses.
        left_paren = res_str.find('(') + 1
        right_paren = res_str.find(')')

        # Split response substring by comma.
        s = res_str[left_paren:right_paren].split(',')

        # Join host on period.
        host_addr = '.'.join(s[0:4])

        return host_addr, int(s[4]), int(s[5])

    def display_incoming_data(self):
        # Accept the connection.
        conn, addr = self.data_sock.accept()

        incoming_data = True
        while incoming_data:
            # Reveive incoming data.
            data = conn.recv(4096)

            # Test if data was received.
            if data:
                System.display(data)
            else:
                incoming_data = False

    def send_pasv_cmd(self):
        pasv_str = 'PASV'

        # Send PASV command.
        self.socket.send((pasv_str + '\r\n').encode())
        self.log_msg_sent(pasv_str)

        # Get server response.
        res = self.get_server_response()
        self.log_res_received(res)

        return res

    # def send_port_cmd(self):
        # host_name = socket.gethostname()
        # host_addr = socket.gethostbyname(host_name)
        # port_str = 'PORT {0},{1},{2}'.format(
        #     host_addr.replace('.', ','), self.DATA_P1, self.DATA_P2)
        # print('port_str: ' + port_str)

        # # Send PORT command.
        # self.socket.send((port_str + '\r\n').encode())
        # self.log_msg_sent(port_str)

        # # Get server response.
        # print('waiting for port reply...')
        # res = self.get_server_response()
        # self.log_res_received(res)

    def run_help(self):
        # Display the list of available commands.
        System.display('Some commands are abbreviated: ')
        System.display_list(self.AVAIL_CMDS)

    def run_list(self, args):
        dirs = ''
        if len(args) > 1:
            dirs = ' '.join(args[1:])

        list_str = 'LIST ' + dirs

        # Send PASV command.
        pasv_res = self.send_pasv_cmd()

        # Open data channel.
        self.open_data_chan(pasv_res)

        # Get server response.
        res = self.data_sock.recv(2048)
        self.log_res_received(res)

        # # Send PORT command.
        # self.send_port_cmd()

        # Send list command.
        self.socket.send((list_str + '\r\n').encode())
        self.log_msg_sent(list_str)

        # Display the requested data.
        print('skipping data retieval')
        exit('')
        # self.display_incoming_data()

        # Get server response.
        res = self.get_server_response()
        self.log_res_received(res)

        return res

    def run_pwd(self, args):
        pwd_str = 'PWD'

        # Send PWD command.
        self.socket.send((pwd_str + '\r\n').encode())
        self.log_msg_sent(pwd_str)

        # Get server response.
        res = self.get_server_response()
        self.log_res_received(res)

        # Parse reply code.
        reply_code = self.parse_reply_code(res)

        # Test if code indicates success.
        if reply_code == self.PATHN_CREATED:
            # Parse the current directory from response.
            pwd = res.decode().split('"')[1]
            System.display(pwd)

        else:
            System.display(
                'There was an error while retieving the current directory.')

        return res

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

    def credentials_needed(self, res):
        return self.parse_reply_code(res) == self.NEW_USER

    def login_successful(self, res):
        return self.parse_reply_code(res) == self.LOGGED_IN

    def get_server_response(self):
        return self.socket.recv(2048)

    def log_msg_sent(self, msg):
        self.logger.write_log('Sent: ' + msg)

    def log_res_received(self, res):
        self.logger.write_log('Received: ' + repr(res))


if __name__ == '__main__':
    main()
