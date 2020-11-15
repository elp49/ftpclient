class Error(Exception):
    '''Base class for exceptions in the FTP Client module.'''
    pass

class ServerReplyError(Error):
    '''Exception raise for errors in the server reply.
    
    Attributes:
        response -- server response in which the error occurred
        message -- explanation of the error 
    '''

    def __init__(self, response, message):
        self.response = response
        self.message = message

    def __str__(self):
        return f'{repr(self.response)} -> {self.message}'
