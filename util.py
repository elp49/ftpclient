#!/usr/bin/env python3
# CS472 - Homework #4
# Edward Parrish
# util.py
#
# This module is the utility module of the FTP server. It provides helper
# functions for the major module.

import sys
from getpass import getpass
import math

DEFAULT_PORT = 21


class System:
    '''System
    This class provides the FTP client with common system helper functions.'''

    @staticmethod
    def args():
        '''args() -> (host address, log filename, port number)
        Retrieve the command line arguments for the FTP server. Handles
        potential errors with the FTP server command line arguments. If errors
        exist then the program exits.'''

        num_args = len(sys.argv)

        # Test if no host address given.
        if num_args < 2:
            System.arg_error('host address argument is required.')

        # Test if no log filename give.
        elif num_args < 3:
            System.arg_error('log filename argument is required')

        # Test if port is specified.
        elif num_args >= 4:
            try:
                # Test if port can be casted to int
                port = int(sys.argv[3])
            except ValueError:
                System.arg_error(
                    'optional port number argument must be a positive integer')
        else:
            port = DEFAULT_PORT

        return (sys.argv[1], sys.argv[2], port)

    @staticmethod
    def arg_error(message):
        '''arg_error(message)
        Write an argument error message to the console and exit.'''

        print(message)
        System.terminate(True)

    @staticmethod
    def get_username(host, port):
        '''get_username(host, port) -> username
        Prompt the user for a username.'''

        # TODO: uncomment below code.
        # username = ''

        # while not username:
        #     username = input(f'User ({host}:{port}): ')

        # return username
        return 'cs472'

    @staticmethod
    def get_password():
        '''get_password() -> password
        Prompt the user for a password.'''

        # TODO: uncomment below code.
        # password = getpass('Password: ')

        # return password
        return 'hw2ftp'

    @staticmethod
    def display(s=''):
        print(s)

    @staticmethod
    def display_list(l):
        '''display_list(l)
        Display a columnized list to the console.'''

        line = ''
        num_items = len(l)
        num_cols = 3
        num_rows = math.ceil(num_items/num_cols)
        item_index = 0
        for i in range(num_rows):
            for _ in range(num_cols):
                if item_index < num_items:
                    line += l[item_index] + '\t\t'
                    item_index += num_rows
            if i < num_rows - 1:
                line += '\n'
                item_index = i + 1

        print(line)

    @staticmethod
    def input(prompt='ftp> '):
        return input(prompt).strip()

    @staticmethod
    def terminate(is_arg_error=False):
        '''terminate(is_arg_error=False)
        Terminate the program. If the termination is due to an argument error,
        then write the correct usage of the program to the console.'''

        if is_arg_error:
            print('Usage: ftpclient [HOST] [FILENAME] [Optional: PORT]')

        exit()
