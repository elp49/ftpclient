# CS472 - Homework #4
# Edward Parrish
# logger.py
#
# This module is the logger module of the FTP Client. It contains the Logger
# class which is used by the major module.

import datetime


class Logger:
    '''Logger
    The Logger helper class. Used to write log messages to a log file.'''
    
    LINE_SEP = '\n'

    def __init__(self, filename):
        self.filename = filename

    def timestamp(self):
        '''timestamp() - > formatted timestamp
        Return a formatted timestamp string of the current datetime.'''

        return datetime.datetime.now().strftime('%x %X.%f')

    def write(self, message):
        '''write(message)
        Write a log message to log file.'''

        line = f'{self.timestamp()} {message}{self.LINE_SEP}'

        # Test if filename is defined.
        if self.filename:
            try:
                # Append the line to log file.
                with open(self.filename, 'a') as f:
                    f.write(line)

            except:
                pass
