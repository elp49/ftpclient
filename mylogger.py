# CS472 - Homework #2
# Edward Parrish
# mylogger.py
#
# This module is the logger module of the ftp client. It contains a Logger class
# that is used by the major module to handle logging.

import datetime


"""Logger
The Logger helper class. Used to write logs to a file.
"""


class Logger:
    line_sep = '\n'

    def __init__(self, filename):
        self.filename = filename

    """get_datetime_str()
    Uses the datetime library to return a custom formatted string of the current
    datetime.
    """

    def get_datetime_str(self):
        return datetime.datetime.now().strftime('%x %X.%f')

    """write_log(log_str)
    Writes the string passed to it in log_str to a new line in the logger's log 
    file preceded by the current datetime string. If the filename has been lost,
    then prints to the console.
    """

    def write_log(self, log_str):
        # Append line separator, datetime, and log string to line.
        line = self.get_datetime_str() + ' ' + str(log_str) + self.line_sep

        # Test if filename is defined.
        if self.filename is not None and len(self.filename) > 0:
            try:
                with open(self.filename, 'a') as log_file:
                    # Append the line to log file.
                    log_file.write(line)

            except Exception as err:
                print('There was an error while writing to the log file {0}: {1}'.format(
                    self.filename, err))
        else:
            print(line)
