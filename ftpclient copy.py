#!/usr/bin/env python3
# CS472 - Homework #4
# Edward Parrish
# ftpclient.py
#
# This module is the major module of the FTP client. It containes the main
# processing loop that receives command line input from the user .

import util
from logger import Logger
import socket

# When set to True, prints FTP activity to console.
VERBOSE = True


def main(client):
    '''main(client)
    The main processing loop that serves the FTP client by accepting user input
    and passing the command along to the client's execute function.'''

    # Test if server response indicates user credentials are needed.
    if client.credentials_needed(res):
        # Get user credentials from user.
        user, pswd = util.System.get_account_info(host, port)

        # Send credentials to server.
        res = client.login(user, pswd).decode()

        # Test if login was unsuccessful.
        if (not client.login_successful(res)):
            # Display error and terminate processing.
            self.logger.write(f'Server response: {err}')
            util.System.exit_()
    else:
        self.logger.write(f'Server response: {err}')
        util.System.exit_()

    util.System.display('Login Successful.')

    # The main processing loop.
    is_quit = False
    while not is_quit:
        # Get list user input args stripped of all whitespace.
        args = util.System.input_args()

        if len(args) > 0:
            is_quit = client.run(args)


class Client:
    '''The FTP client which establishes control and data connections with
    servers. It uses the Logger class to write server responses to and the
    System class to perform I/O.'''

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

    AVAILABLE_CMDS = [QUIT, HELP, LIST, PWD, CWD, GET, PUT]

    def __init__(self, logger):
        self.logger = logger
        self.host = None
        self.port = None
        self.conn = None # socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_conn = None

    def execute(self):
        if not conn:
            return

    def connect(self, addr):
        '''connect(addr) -> boolean
        If the client is not already connected to a host, then attempt to
        establish a connection to the given address. If the connection is
        successful, then return True; otherwise return False.'''

        # Connect to host on given port.
        self.logger.write(f'Connecting to {host}:{port}.')
        try:
            self.conn.connect((host, port))

            # # Get server response.
            # res = self.get_server_response()
            # self.log_res_received(res)

        except OSError, socket.gaierror, TimeoutError  as err:
            self.logger.write(f'A timeout error occurred: {err}')
            util.System.exit_()

        return res

    def addr_ok(self, addr):
        '''addr_ok(addr) -> (host address, port number)
        Perform various checks on '''

    def disconnect(self):
        '''disconnect()
        Sends the QUIT command to the server and logs response.'''

        discon_str = 'QUIT'

        # Send quit.
        self.conn.send((discon_str + '\r\n').encode())
        self.log_msg_sent(discon_str)

        # Get server response.
        res = self.get_server_response() # 221 Goodbye.
        self.log_res_received(res)

    def login(self, user, pswd=None):
        '''login(user, pswd)
        Attempts to perform user login by sending the USER command with the
        given username. If the server responds with code 331 Password needed,
        then sends the PASS command with the given password.'''
        
        res = None
        user_str = f'USER {user}'

        try:
            # Send username.
            self.conn.send((user_str + '\r\n').encode())
            self.log_msg_sent(user_str)

            # Get server response.
            res = self.get_server_response()
            self.log_res_received(res)

            # Test if reply code indicates password needed.
            if self.parse_reply_code(res) == self.PASSWORD_NEEDED:
                # Test if password is given.
                if pswd is not None:
                    pass_str = f'PASS {pswd}'

                    # Send password.
                    self.conn.send((pass_str + '\r\n').encode())
                    self.log_msg_sent(pass_str)

                    # Get server response.
                    res = self.get_server_response()
                    self.log_res_received(res)

                else:
                    self.logger.write(
                        'A password is required for account.')
                    util.System.exit_()

        except Exception as err:
            self.logger.write(f'An error occurred: {err}')
            util.System.exit_()

        return res

    def parse_reply_code(self, res):
        '''parse_reply_code(res) -> reply code
        Decodes a server response and parse the reply code number. Returns the
        resulting reply code as an integer.'''

        code = None

        if res:
            # Test response data type.
            if isinstance(res, bytes):
                res_str = res.decode().strip().split(' ')[0]

            elif isinstance(res, str) and len(res) > 0:
                res_str = res.strip().split(' ')[0]

            try:
                # Cast code to int.
                code = int(res_str)

            except Exception:
                self.logger.write('Server reply code unkown.')
                util.System.exit_()

        return code

    # run(args)
    # Determines which command the user entered and runs that command's function.
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

                # PASV, EPSV, PORT, EPRT, RETR, STOR, SYST

        return is_quit

    # open_data_chan(pasv_res)
    # Opens a connection to the server's data port.
    def open_data_chan(self, pasv_res):
        # Parse host and port.
        host_addr, p1, p2 = self.parse_host_and_port(pasv_res)

        # Connect to host data port.
        self.data_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_conn.connect((host_addr, (p1*256) + p2))

    # parse_host_and_port()
    # Parse the host and port from the server response of the PASV command.
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

    # send_pasv_cmd()
    # Send the PASV command to the server to enter passive mode.
    def send_pasv_cmd(self):
        pasv_str = 'PASV'

        # Send PASV command.
        self.conn.send((pasv_str + '\r\n').encode())
        self.log_msg_sent(pasv_str)

        # Get server response.
        res = self.get_server_response()
        self.log_res_received(res)

        return res

    # run_help()
    # Displays the help menu.
    def run_help(self):
        # Display the list of available commands.
        util.System.display('Some commands are abbreviated: ')
        util.System.display_list(self.AVAILABLE_CMDS)

    # run_list()
    # Attempts establish a data connection with the server so that it may
    # list the contents of the current directory.
    #
    # Note: this function is likely to cause a timeout error.
    def run_list(self, args):
        dirs = ''
        if len(args) > 1:
            dirs = ' '.join(args[1:])

        list_str = 'LIST ' + dirs

        # Send PASV command.
        pasv_res = self.send_pasv_cmd()

        try:
            # Open data channel.
            self.open_data_chan(pasv_res)

            # Get server response.
            res = self.data_conn.recv(2048)
            self.log_res_received(res)

            # Send list command.
            self.conn.send((list_str + '\r\n').encode())
            self.log_msg_sent(list_str)

            # Get server response.
            res = self.get_server_response()
            self.log_res_received(res)

        except Exception:
            util.System.display(
                "An error occured while attempting to list the directory")

        return res

    # run_pwd()
    # Sends the PWD command to the server and if successful displays the
    # working directory response.
    def run_pwd(self, args):
        pwd_str = 'PWD'

        # Send PWD command.
        self.conn.send((pwd_str + '\r\n').encode())
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
            util.System.display(pwd)

        else:
            util.System.display(
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

    # is_quit(cmd)
    # Determines if the given command is quit.
    def is_quit(self, cmd):
        return cmd.lower() == self.QUIT.lower()

    # is_help(cmd)
    # Determines if the given command is help.
    def is_help(self, cmd):
        return cmd.lower() == self.HELP.lower()

    # is_list(cmd)
    # Determines if the given command is list.
    def is_list(self, cmd):
        return cmd.lower() == self.LIST.lower()

    # is_pwd(cmd)
    # Determines if the given command is pwd.
    def is_pwd(self, cmd):
        return cmd.lower() == self.PWD.lower()

    # is_cwd(cmd)
    # Determines if the given command is cwd.
    def is_cwd(self, cmd):
        return cmd.lower() == self.CWD.lower()

    # is_get(cmd)
    # Determines if the given command is get.
    def is_get(self, cmd):
        return cmd.lower() == self.GET.lower()

    # is_put(cmd)
    # Determines if the given command is put.
    def is_put(self, cmd):
        return cmd.lower() == self.PUT.lower()

    # credentials_needed(res)
    # Determines if the response indicates that credentials are needed.
    def credentials_needed(self, res):
        return self.parse_reply_code(res) == self.NEW_USER

    # login_successful(res)
    # Determines if the response indicates that loggin was successful.
    def login_successful(self, res):
        return self.parse_reply_code(res) == self.LOGGED_IN

    # get_server_response()
    # Returns the server response.
    def get_server_response(self):
        return self.conn.recv(2048)

    # log_msg_sent(msg)
    # Write to the log file the message sent.
    def log_msg_sent(self, msg):
        self.logger.write('Sent: ' + msg)

    # log_res_received(res)
    # Writes to the log file the received response.
    def log_res_received(self, res):
        self.logger.write('Received: ' + repr(res))


if __name__ == '__main__':
    # Get command line args.
    host, filename, port = util.System.args()


    # Initialize logger and client objects.
    logger = Logger(filename, VERBOSE)
    client = Client(logger)

    # Connect client to host and begin main processing loop.
    client.connect((host, port))
    main(client)
