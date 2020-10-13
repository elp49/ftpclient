#!/usr/bin/env python3
# CS472 - Homework #2
# Edward Parrish
# systemhelper.py
#
# This module is the system helper module of the ftp client. It contains a the
# functions needed to communicate with the client system and is used by the 
# major module.

import sys

"""get_ftp_args()
Handles potential errors with the ftp client command line arguments. If errors 
exist then the program exits. Otherwise, returns an array of the ftp client
arguments as a string in the form: [<HOST>, <FILENAME>, <PORT>]
"""


def get_ftp_args():
    DEFAULT_PORT = 21
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
            exit_('optional port number argument must be a positive integer (the default is ' +
                  DEFAULT_PORT + ').')
    else:
        port = DEFAULT_PORT

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
