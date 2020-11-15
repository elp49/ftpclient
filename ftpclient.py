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

    # Create thread to automatically receive and queue responses from server.
    t = threading.Thread(target=client.recvall)
    t.start()

    # Test if client is not logged in.
    if not client.logged_in:
        # Get server response: 220 Ready for new user.
        while True:
            response = client.get_response()
            if response.code == SERVICE_READY:
                break

        # Perform login with USER and PASS commands.
        client.login()

    wait = System.input()
    # while True:
    #     # Get user option.
    #     args = System.input_args()

    #     if len(args) > 0:
    #         is_quit = client.run(args)


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


class Response:

    def __init__(self, res):
        self.code, self.message = self.parse(res)

    def __str__(self):
        return f'{self.code} {self.message}'

    def parse(self, response):
        '''parse(response) -> (reply code, message)
        Parse the server response code and message.'''

        # Test if response has not been decoded.
        if isinstance(response, bytes):
            res = decode(response).strip()
        else:
            res = response.strip()

        # Test if reply code has a message attached.
        i = res.find(' ')
        if i > 0:
            # Parse reply code and message.
            code = res[:i]
            message = res[(i+1):]
        else:
            code = res

        # Test if reply code is positive integer.
        try:
            code = int(code)
            if code < 0:
                raise ServerReplyError(
                    res, "Server reply code is not a positive integer.")
        except ValueError:
            raise ServerReplyError(
                res, "Server response does not start with reply code integer.")

        return code, message


SERVICE_READY = 220
USER_LOGGED_IN = 230
PASSWORD_NEEDED = 331


class Client:

    def __init__(self):
        self.conn = None
        self.logged_in = False
        self.response_queue = []
        self.response_event = threading.Event()

    def connect(self, addr):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((host, port))

    def close(self):
        self.sendall('QUIT')
        self.conn.close()

    def sendall(self, command, value=''):
        '''sendall(command, value='')
        Send a command to the server.'''

        msg = f'{command} {value}'
        self.conn.sendall(encode(f'{msg}\r\n'))
        log(f'Sent: {msg}')

    def recvall(self, bufsize=4096):
        '''recvall(bufsize=4096)
        Continuously wait for response data from server. When a response is
        receiveed, decode it and add it to client's response queue.'''

        try:
            data = b''
            while True:
                # Receive some data.
                res = self.conn.recv(bufsize)
                data += res

                # Test if end of message.
                if len(res) < bufsize:
                    # Test for bad server reply.
                    try:
                        response = Response(res)

                        # TODO: remove this.
                        print(response)

                        log(f'Received: {response}')

                        # Append data to client's response queue.
                        self.add_response(response)
                    except ServerReplyError as err:
                        self.handle_bad_server_reply()
                        print(err)

                    data = b''

        except KeyboardInterrupt:
            print('keyboard interrupt - probably thread')
            System.terminate()

    def handle_bad_server_reply(self):
        print('The server sent a bad reply. It will be ignored.')

    def add_response(self, response):
        # Add server response to response queue.
        self.response_queue.append(response)

        # Test if response event is not set.
        if not self.response_event.isSet():
            self.response_event.set()

    def get_response(self):
        # Wait for server response.
        if not self.response_queue:
            self.response_event.wait()

        res = self.response_queue.pop(0)

        # Test if response queue is empty.
        if not self.response_queue:
            self.response_event.clear()

        return res

    def login(self):
        '''login()
        Prompt the user for username and password. Attempt to perform user login
        by sending the USER and PASS commands to the server.'''

        username = System.get_username(host, port)
        # Send USER command and get server response.
        self.sendall('USER', username)
        response = self.get_response()

        # Test if server reply code indicates password needed.
        if response.code == PASSWORD_NEEDED:
            password = System.get_password()
            if password:
                # Send password and get server response.
                self.sendall('PASS', password)
                response = self.get_response()

            else:
                log('A password is required for account.')
                System.terminate()

        self.logged_in = True


if __name__ == '__main__':
    # Get command line args and initialize logger object..
    # host, filename, port = System.args()
    host, filename, port = '10.246.251.93', 'mylog.txt', 21
    logger = Logger(filename)

    while True:
        # Connect client to host and begin main processing loop.
        client = Client()
        try:
            client.connect((host, port))
        except:
            log("Unable to establish a connection with host.")
            print("Unable to establish a connection with host.")
            System.terminate()

        try:
            main(client, host, port)
        except KeyboardInterrupt:
            print('a keyboard interrupt - maybe main?')
            client.close()
            System.terminate()
        except:
            log("An error occurred while connected to host, restarting service.")
            print("An error occurred while connected to host, restarting service.")
            client.close()
