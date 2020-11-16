#!/usr/bin/env python3
# CS472 - Homework #4
# Edward Parrish
# ftpclient.py
#
# This module is the major module of the FTP client. It containes the main
# processing loop that receives command line input from the user .

from util import System
from logger import Logger
from exceptions import ServerReplyError
import socket
import threading

global logger
DEFAULT_ENCODING = 'ISO-8859-1'


def main(client, host, port):
    '''main(client)
    The main processing loop of the FTP Client.'''

    # Test if client is not logged in.
    if not client.logged_in:
        # Get server response: 220 Ready for new user.
        while True:
            response = client.get_response()
            if response.code == SERVICE_READY:
                break

        # Perform login with USER and PASS commands.
        client.login()

    while True:
        # Get user command and execute it.
        command, value = get_user_command()
        client.execute(command, value)


def get_user_command():
    '''get_user_command() -> (command, value)
    Get user command to be performed. If command is followed by values, then
    parse them.'''

    # Get user input.
    while True:
        try:
            user_input = System.input()
            if user_input:
                break
        except KeyboardInterrupt:
            pass

    # Test if command has values.
    i = user_input.find(' ')
    if i > -1:
        command = user_input[:i]
        value = user_input[(i+1):]
    else:
        command = user_input
        value = ''

    return command, value


def log(message):
    '''log(message)
    Write a log message.'''

    if logger:
        logger.write(message)


def encode(data, encoding='utf-8'):
    try:
        return data.encode(encoding)
    except UnicodeEncodeError:
        return data.encode(DEFAULT_ENCODING)


def decode(data, encoding='utf-8'):
    try:
        return data.decode(encoding)
    except UnicodeDecodeError:
        return data.decode(DEFAULT_ENCODING)


class ServerResponse:

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return f'{self.code} {self.message}'


SERVICE_READY = 220
USER_LOGGED_IN = 230
PASSWORD_NEEDED = 331


class Client:

    def __init__(self):
        self.conn = None
        self.logged_in = False
        self.verbose = True

    def connect(self, host, port):
        hostaddr = socket.gethostbyname(host)
        hostname = socket.gethostbyaddr(hostaddr)[0]
        log(f'Connecting to {hostname} ({hostaddr}). ')
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((host, port))

    def close(self):
        self.send_message('QUIT')
        self.conn.close()

    def send_message(self, command, value=''):
        '''send_message(command, value='')
        Send a command to the server.'''

        msg = f'{command} {value}'
        self.conn.sendall(encode(f'{msg}\r\n'))
        log(f'Sent: {msg}')

    def get_response(self, bufsize=4096):
        '''get_response(bufsize=4096) -> ServerResponse
        Receive a response from the server. Parse the reply code and message.'''

        data = b''
        while True:
            # Receive some data.
            response = self.conn.recv(bufsize)
            data += response

            # Test if end of message.
            if len(response) < bufsize:
                # Test for bad server reply.
                try:
                    res = self.parse_server_response(response)
                except ServerReplyError as err:
                    self.handle_bad_server_reply(err)

                break

        if self.verbose:
            System.display(res)

        log(f'Received: {res}')
        return res

    def parse_server_response(self, response):
        '''parse_server_response(response) -> ServerResponse
        Parse the server reply code and message.'''

        # Test if response is empty.
        if not response:
            return ''

        # Test if response has not been decoded.
        if isinstance(response, bytes):
            res = decode(response).strip()
        else:
            res = response.strip()

        # Test if response doesn't start with 3-digit reply code.
        res_len = len(res)
        num_digits = 3
        if res_len < num_digits:
            raise ServerReplyError(
                res, 'Server response does not start with a 3-digit reply code')

        # Parse reply code and message.
        code_str = res[:num_digits]
        # Test if response has a message.
        if res_len > num_digits+1:
            message = res[(num_digits+1):]
        else:
            message = ''

        # Test if reply code is positive integer.
        try:
            code = int(code_str)
            if code < 0:
                raise ServerReplyError(
                    res, 'Server reply code is not a positive integer.')
        except ValueError:
            raise ServerReplyError(
                res, 'Server response does not start with a 3-digit reply code.')

        return ServerResponse(code, message)

    def handle_bad_server_reply(self, error):
        System.display(f'Error: {repr(error)}')
        System.display('The server sent a bad reply. It will be ignored.')

    def login(self):
        '''login()
        Prompt the user for username and password. Attempt to perform user login
        by sending the USER and PASS commands to the server.'''

        # Prompt user for username.
        username = System.get_username(host, port)

        # Send USER command with username and get server response.
        self.send_message('USER', username)
        response = self.get_response()

        # Test if server reply code indicates password needed.
        if response.code == PASSWORD_NEEDED:
            # Prompt user for password.
            password = System.get_password()
            if password:
                # Send password and get server response.
                self.send_message('PASS', password)
                response = self.get_response()

            else:
                log('A password is required for account.')
                System.terminate()

        self.logged_in = True

    def execute(self, command, value=''):

        cmd = command.lower()
        if cmd in USER_COMMANDS:
            if cmd == CWD:
                self.cwd(value)
            elif cmd == PWD:
                self.pwd()
            elif cmd == LIST:
                self.ls(value)
            # PASV, EPSV, PORT, EPRT,
            # RETR, STOR, LIST.
            elif cmd == SYST:
                self.syst()
            elif cmd == HELP:
                self.help()
            elif cmd == QUIT:
                self.quit()
            elif cmd == VERBOSE:
                self.toggle_verbose()
        else:
            System.display('Invalid command')
            

    def cwd(self, path=''):
        # Test if no path given.
        if not path:
            try:
                path = System.input('Remote directory ')
            except KeyboardInterrupt:
                pass
            
        # Test if user entered a path.
        if path:
            self.send_message('CWD', path)
            self.get_response()
        else:
            System.display('Usage: cd remote directory')

    def pwd(self):

        self.send_message('PWD')
        response = self.get_response()

        # Test if verbose mode is turned off.
        if not self.verbose:
            System.display(response)

    def ls(self, value=''):

        self.send_message('PASV')
        # do active / passive shit.
        self.send_message(f'LIST {value}')
        response = self.get_response()


    def syst(self):
        '''syst()
        Send the SYST comand to server and receive system information in 
        response. Display the system information to console.'''

        self.send_message('SYST')
        response = self.get_response()

        # Test if verbose mode if turned off.
        if not self.verbose:
            System.display(response)

    def help(self):
        '''help()
        Display the sorted list of user commands to the console.'''

        commands = USER_COMMANDS
        commands.sort()
        System.display('Some commands are abbreviated.  Commands are:\n')
        System.display_list(commands)

    def quit(self):
        '''quit()
        Close the connection and terminate the FTP Client.'''

        System.display()
        self.close()
        System.terminate()

    def toggle_verbose(self):
        '''toggle_verbose()
        Toggle verbose mode on or off. When verbose mode is turned on, then
        server responses are displayed to the console upon retreval.'''

        #Verbose mode Off .
        if self.verbose:
            self.verbose = False
            System.display('Verbose mode Off .')
        else:
            self.verbose = True
            System.display('Verbose mode On .')


CWD = 'cd'
PWD = 'pwd'
LIST = 'ls'
RETR = 'get'
STOR = 'put'
SYST = 'system'
HELP = 'help'
QUIT = 'quit'

VERBOSE = 'verbose'

USER_COMMANDS = [CWD, PWD, LIST, RETR, STOR, SYST, HELP, QUIT, VERBOSE]


if __name__ == '__main__':
    # Get command line args and initialize logger object..
    # host, filename, port = System.args()
    # host, filename, port = '10.246.251.93', 'mylog.txt', 21
    host, filename, port = '127.0.0.1', 'mylog.txt', 2121
    logger = Logger(filename)

    while True:
        # Connect client to host and begin main processing loop.
        client = Client()
        try:
            client.connect(host, port)
        except:
            log("Unable to establish a connection with host.")
            System.display("Unable to establish a connection with host.")
            break

        try:
            main(client, host, port)
        except KeyboardInterrupt as err:
            System.display(
                f'a keyboard interrupt from if __name__==__main__: -> \r\n{repr(err)}')
            client.close()
            break
        except Exception as err:
            log(
                f"An error occurred while connected to host, restarting service -> \r\n{repr(err)}")
            System.display(
                f"An error occurred while connected to host, restarting service -> \r\n{repr(err)}")
            client.close()
