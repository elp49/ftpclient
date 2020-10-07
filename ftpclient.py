#!/usr/bin/env python3
# CS472 - Homework #2
# Edward Parrish
# ftpclient.py
#
# This module is the major module of the FTP client, with the main processing loop.

import sys
import socket
from mylogger import Logger

"""main()
The main processing loop of the FTP client. It initiates the TCP scoket and
begins the conersation for the FTP server.
"""


def main():
    # Get command line args
    host, filename, port = get_sys_args()

    # Create a logger instance with log filename.
    logger = Logger(filename)
    logger.write_log('Connecting to ' + host + ' on port ' + str(port) + '.')

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
            sock.sendall(b'Yo')
            data = sock.recv(1024)
            print('Got: ' + repr(data))
    except TimeoutError as err:
        exit_('A timeout error occurred: {0}'.format(err))


"""get_sys_args()
Handles potential errors with the command line args. If errors exist with the
args then the program exits. Otherwise, returns an array of the system args as
string in the form: [<HOST>, <FILENAME>, <PORT>]
"""


def get_sys_args():
    num_args = len(sys.argv)

    # Test if no host given.
    if num_args < 2:
        exit_('host argument is required.')

    # Test if no log filename give.
    elif num_args < 3:
        exit_('log filename argument is required')

    # Test if port is specified.
    elif num_args >= 4:
        try:
            # Test if port can be casted to int
            port = int(sys.argv[3])
        except ValueError:
            exit_('port number must be a positive integer (default is 21).')
    else:
        port = 21

    return [sys.argv[1], sys.argv[2], port]


"""exit_(msg)
Prints the error message passed to it by msg to the console and then exits. If 
the optional argument isArgErr is passed as True, then the correct usage of the 
program is also displayed before exiting.
"""


def exit_(msg, isArgErr=False):
    print('Error: ' + msg)

    if isArgErr:
        print('Usage: ftpclient <HOST> <FILENAME> [Optional: <PORT>]')

    exit('exiting')


if __name__ == '__main__':
    main()
