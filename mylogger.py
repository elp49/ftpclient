# CS472 - Homework #2
# Edward Parrish
# mylogger.py
#
# This module is the logger module of the ftp client. It contains a logger class
# that is used by the major module to handle logging.

import datetime


"""Logger
The Logger helper class. Used to write logs to a file.
"""


class Logger:
    line_sep = '\n'

    def __init__(self, filename):
        self.filename = filename

    """get_date_str()
    Uses the datetime library to return a custom formatted datetime string of 
    the current time.
    """

    def get_date_str(self):
        return datetime.datetime.now().strftime('%x %X.%f')

    """write_log(log_str)
    Writes the string passed to it in log_str to a new line in the logger's log 
    file preceded by the current datetime string. If the filename has been lost,
    then prints to the console.
    """

    def write_log(self, log_str):
        line = self.get_date_str() + ' ' + log_str

        # Test if filename is defined.
        if self.filename is not None and len(self.filename) > 0:
            with open(self.filename, 'a') as log_file:
                log_file.write(self.line_sep + line)
        else:
            print(self.line_sep + line)
