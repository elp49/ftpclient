#!/usr/bin/env python3
# CS472 - Homework #2
# Edward Parrish
# systemhelper.py
#
# This module is the system helper module of the ftp client. It contains a the
# functions needed to communicate with the client system and is used by the
# major module.

import sys
import getpass


class System:
    """get_ftp_args()
    Handles potential errors with the ftp client command line arguments. If errors 
    exist then the program exits. Otherwise, returns an array of the ftp client
    arguments as a string in the form: [<HOST>, <FILENAME>, <PORT>]
    """

    @staticmethod
    def get_ftp_args():
        num_args = len(sys.argv)

        # Test if no host given.
        if num_args < 2:
            System.exit_('host argument is required.')

        # Test if no log filename give.
        elif num_args < 3:
            System.exit_('log filename argument is required')

        # Test if port is specified.
        elif num_args >= 4:
            try:
                # Test if port can be casted to int
                port = int(sys.argv[3])
            except ValueError:
                System.exit_('optional port number argument must be a positive integer')
        else:
            port = None

        return [sys.argv[1], sys.argv[2], port]


    """get_account_info()
    Prompt the user for and return a username and password.
    """
    @staticmethod
    def get_account_info(host, port):
        #TODO: uncomment below code.
        # user = ''

        # while len(user) < 1:
        #     user = input('User ({0}:{1}): '.format(host, port))

        # pswd = getpass.getpass('Password: ')

        # return user, pswd
        return 'cs472', 'hw2ftp'

    @staticmethod
    def display(s):
        print(s)

    @staticmethod
    def display_list(l):
        mylist = l
        mylist.sort()

        line = ''
        for s in mylist:
            line += s + '\t\t'
        
        print(line)

    @staticmethod
    def input(s=None):
        try:
            # Test if s is None.
            if s is None:
                result = input()
            else:
                result = input(s)

        except KeyboardInterrupt:
            System.exit_('KeyboardInterrupt')

        return result.strip()

    @staticmethod
    def input_args(s=None):
        result = []

        # Get raw input args.
        raw = System.input(s).split(' ')

        for a in raw:
            a = a.strip()
            if len(a) > 0:
                result.append(a)

        return result



    """exit_(msg)
    Prints the error message passed to it by msg to the console and then exits. If 
    the optional argument isArgErr is passed as True, then the correct usage of the 
    program is also displayed before exiting.
    """


    @staticmethod
    def exit_(msg, isArgErr=False):
        print('Error: ' + msg)

        if isArgErr:
            print('Usage: ftpclient <HOST> <FILENAME> [Optional: <PORT>]')

        exit('exiting')
