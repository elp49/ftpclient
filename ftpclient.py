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

IPv4 = 1
IPv6 = 2
NET_PRTS = [IPv4, IPv6]

FILE_STATUS_OK = 150
SERVICE_READY = 220
FILE_ACTION_SUCCESSFUL = 226
USER_LOGGED_IN = 230
PASSWORD_NEEDED = 331
TIMEOUT = 421
COMMAND_NOT_IMPLEMENTED = 502


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


class Client:

    def __init__(self, host, port):
        self.conn = None
        self.host = host
        self.port = port
        self.logged_in = False
        self.verbose = True
        self.use_pasv = True
        self.use_epsv = False
        self.use_port = False
        self.use_eprt = False

    def connect(self):
        hostaddr = socket.gethostbyname(self.host)
        hostname = socket.gethostbyaddr(hostaddr)[0]
        log(f'Connecting to {hostname} ({hostaddr}). ')
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.host, self.port))

    def close(self):
        if self.conn:
            try:
                self.send_message('QUIT')
                self.conn.close()
            except:
                pass
            self.conn = None

    def send_message(self, command, value=''):
        '''send_message(command, value='')
        Send a command to the server.'''

        msg = f'{command} {value}'
        self.conn.sendall(encode(f'{msg}\r\n'))
        log(f'Sent: {msg}')

    def get_response(self, bufsize=4096):
        '''get_response(bufsize=4096) -> ServerResponse
        Receive a response from the server. Parse the reply code and message.'''

        # byte_data = b''
        # while True:
        #     # Receive some data.
        #     res = self.conn.recv(bufsize)
        #     byte_data += res

        #     # Test if end of message.
        #     if len(res) < bufsize:
        #         break

        byte_data = self.conn.recv(bufsize)
        # Test for bad server reply.
        try:
            response = self.parse_server_response(byte_data)
        except ServerReplyError as err:
            self.handle_bad_server_reply(err)

        if self.verbose:
            System.display(response)

        log(f'Received: {response}')

        # Test if response indicates a timeout.
        if response.code == TIMEOUT:
            System.display('Connection closed by remote host.')

        return response

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

        # Test if command is not in list of user commands.
        cmd = command.lower()
        if cmd not in USER_COMMANDS:
            System.display('Invalid command')

        # Test if command requires a connection but client is not connected.
        elif cmd in CONN_REQUIRED_COMMANDS and not self.conn:
            System.display('Not connected.')

        # Test if command is to set the data connection type.
        elif cmd in DATA_CONN_COMMANDS:
            self.toggle_data_conn_type(cmd)

        # Test if command requires a data connection.
        elif cmd in COMMANDS_THAT_USE_DATA_CONN:
            if cmd == LIST:
                self.ls(value)
            elif cmd == RETR:
                self.retr(value)
            elif cmd == STOR:
                self.stor(value)

        else:
            if cmd == CWD:
                self.cwd(value)
            elif cmd == PWD:
                self.pwd()
            elif cmd == SYST:
                self.syst()
            elif cmd == HELP:
                self.help()
            elif cmd == REMOTE_HELP:
                self.remotehelp()
            elif cmd == QUIT:
                self.quit()
            elif cmd == VERBOSE:
                self.toggle_verbose()

    def cwd(self, path=''):
        # Test if no path given.
        if not path:
            try:
                path = System.input('Remote directory ')
            except KeyboardInterrupt:
                pass

        # Test if user did not enter a path.
        if not path:
            System.display('Usage: cd remote-directory')
        else:
            self.send_message('CWD', path)
            self.get_response()

    def pwd(self):

        self.send_message('PWD')
        response = self.get_response()

        # Test if verbose mode is turned off.
        if not self.verbose:
            System.display(response)

    def ls(self, path=''):
        # Open a data connection using the currently enabled connection type.
        data_conn = self.open_data_conn()
        if not data_conn:
            return

        # Send the LIST command over command channel and get response.
        self.send_message('LIST', path)
        response = self.get_response()

        if response.code == FILE_STATUS_OK or response.message.find(str(FILE_STATUS_OK)) != -1:
            # Retrieve directory listing from data connection.
            data_conn.receive_data()
            response = self.get_response()  # 226 Dir send ok.

        data_conn.close()

    def retr(self, path=''):

        # Test if remote file is not given.
        if not path:
            try:
                remote_path = System.input('Remote file ')
                local_path = System.input('Local file ')
            except KeyboardInterrupt:
                System.display('Usage: get remote-file local-file')
                return

        else:
            i = path.find(' ')
            # Test if only remote path given.
            if i == -1:
                remote_path = path
                try:
                    local_path = System.input('Local file ')
                except KeyboardInterrupt:
                    System.display('Usage: get remote-file local-file')
                    return
            else:
                remote_path = path[:i]
                local_path = path[(i+1):]

        # Test if either remote or local path contains spaces.
        i1 = remote_path.find(' ')
        i2 = local_path.find(' ')
        if i1 != -1 or i2 != -1:
            System.display('Usage: get remote-file local-file')
            return

        # Test if user did not enter remote or local file paths.
        if not remote_path or not local_path:
            System.display('Usage: get remote-file local-file')
        else:
            # Open a data connection using the currently enabled connection type.
            data_conn = self.open_data_conn()
            if not data_conn:
                return

            # Send the RETR command over command channel and get response.
            self.send_message('RETR', remote_path)
            response = self.get_response()

            if response.code == FILE_STATUS_OK or response.message.find(str(FILE_STATUS_OK)) != -1:    
                # Retrieve remote file data over data connection.
                file_content = data_conn.receive_data()

                if response.code == FILE_ACTION_SUCCESSFUL:
                    # Write the local file.
                    System.write_file(local_path, file_content)
                    log(f'File "{local_path}" written.')

            data_conn.close()

    def stor(self, path):

        # Test if local file is not given.
        if not path:
            try:
                local_path = System.input('Local file ')
                remote_path = System.input('Remote file ')
            except KeyboardInterrupt:
                System.display('Usage: put local-file remote-file')
                return

        else:
            i = path.find(' ')
            # Test if only local path given.
            if i == -1:
                local_path = path
                try:
                    remote_path = System.input('Remote file ')
                except KeyboardInterrupt:
                    System.display('Usage: put local-file remote-file')
                    return
            else:
                local_path = path[:i]
                remote_path = path[(i+1):]

        # Test if either local or remote path contains spaces.
        i1 = local_path.find(' ')
        i2 = remote_path.find(' ')
        if i1 != -1 or i2 != -1:
            System.display('Usage: put local-file remote-file')
            return

        # Test if user did not enter local or remote file paths.
        if not local_path or not remote_path:
            System.display('Usage: put local-file remote-file')
        else:
            # Open a data connection using the currently enabled connection type.
            data_conn = self.open_data_conn()
            if not data_conn:
                return

            # Send the STOR command over command channel and get response.
            self.send_message('STOR', remote_path)
            response = self.get_response()

            if response.code == FILE_STATUS_OK or response.message.find(str(FILE_STATUS_OK)) != -1:
                
                # Send local file data over data connection.
                data_conn.send_file(local_path)

                if response.code == FILE_ACTION_SUCCESSFUL:
                    log(f'File "{remote_path}" sent.')

            data_conn.close()

    def syst(self):
        '''syst()
        Send the SYST comand to server and receive system information in 
        response. Display the system information to console.'''

        self.send_message('SYST')
        response = self.get_response()

        # Test if verbose mode if turned off.
        if not self.verbose:
            System.display(response)

    def remotehelp(self):
        '''remotehelp()
        Send the HELP comand to server and receive help information in response.
        Display the help information to console.'''

        self.send_message('HELP')
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

    def open_data_conn(self):
        '''open_data_conn() -> DataConnection
        Create a new DataConnection object and use the currently enabled
        connection type (PASV/EPSV/PORT/EPRT) to establish a connection with
        the server.'''

        data_conn = DataConnection()
        # PASV
        if self.use_pasv:
            self.send_message('PASV')
            response = self.get_response()
            # Test if PASV is disabled.
            if response.code == COMMAND_NOT_IMPLEMENTED:
                System.display('PASV/EPSV is disabled by server.')
                System.display('Use pasv and epsv commands to enable PORT/EPRT')
            else:
                host, port = self.parse_pasv_response(response.message)
                data_conn.connect(host, port, self.address_family())
                return data_conn

        # EPSV
        elif self.use_epsv:
            self.send_message('EPSV')
            response = self.get_response()
            # Test if EPSV is disabled.
            if response.code == COMMAND_NOT_IMPLEMENTED:
                System.display('PASV/EPSV is disabled by server.')
                System.display('Use pasv and epsv commands to enable PORT/EPRT')
            else:
                host, port = self.parse_epsv_response(response.message)
                data_conn.connect(host, port, self.address_family())
                return data_conn

        # PORT
        elif self.use_port:
            h1to4 = self.host.replace('.', ',')
            port = data_conn.bind(self.address_family())
            p1, p2 = self.convert_port_to_p1p2(port)
            self.send_message('PORT', f'{h1to4},{p1},{p2}')
            response = self.get_response()
            # Test if PORT is disabled.
            if response.code == COMMAND_NOT_IMPLEMENTED:
                System.display('PORT/EPRT is disabled by server.')
                System.display('Use port and eprt commands to enable PASV/EPSV')
            else:
                # Create and start new thread to serve the data connection.
                t = threading.Thread(target=data_conn.listen)
                t.start()
                return data_conn

        # EPRT
        elif self.use_eprt:
            net_prt = self.address_family_num()
            client_addr = socket.gethostbyname(socket.gethostname())
            port = data_conn.bind(self.address_family(net_prt))
            self.send_message('EPRT', f'|{net_prt}|{client_addr}|{port}|')
            response = self.get_response()
            # Test if EPRT is disabled.
            if response.code == COMMAND_NOT_IMPLEMENTED:
                System.display('PORT/EPRT is disabled by server.')
                System.display('Use port and eprt commands to enable PASV/EPSV')
            else:
                # Create and start new thread to serve the data connection.
                t = threading.Thread(target=data_conn.listen)
                t.start()
                return data_conn

        return None

    def parse_pasv_response(self, response):
        DELIMETER = ','
        i1 = response.find('(') + 1
        i2 = response.find(')')
        a = response[i1:i2].split(DELIMETER)

        host = '.'.join(a[:4])
        port = self.convert_p1p2_to_port(a[4], a[5])

        return host, port

    def parse_epsv_response(self, response):
        DELIMETER = '|'
        i1 = response.find('(') + 1
        i2 = response.find(')')
        a = response[i1:i2].split(DELIMETER)

        # TODO: check port
        port = int(a[3])

        return self.host, port

    def address_family(self, net_prt=None):
        '''address_family() -> address family
        Get the address family that is represented by the given address family 
        number according to the Address Family Numbers specified in RFC1700.
        This client only supports IPv4 and IPv6. Return None if neither of these
        are the result.'''

        if not net_prt:
            return self.conn.family

        if net_prt == IPv4:
            return socket.AF_INET
        elif net_prt == IPv6:
            return socket.AF_INET6

        return None

    def address_family_num(self, addr_fam=None):
        '''address_family_num() -> address family
        Get the address family number that represents the client's address
        family according to the Address Family Numbers specified in RFC1700.
        This client only supports IPv4 and IPv6. Return None if neither of these
        are the result.'''

        if not addr_fam:
            addr_fam = self.conn.family

        if addr_fam == socket.AF_INET:
            return IPv4
        elif addr_fam == socket.AF_INET:
            return IPv6

        return None

    def convert_port_to_p1p2(self, port):
        '''convert_port_to_p1p2(port) -> (p1, p2)
        Convert a given port number into p1 and p2.'''

        p1 = int(port) // 256
        p2 = int(port) - (p1 * 256)
        return p1, p2

    def convert_p1p2_to_port(self, p1, p2):
        '''convert_p1p2_to_port(p1, p2) -> port
        Convert a given p1 and p2 into a port number.'''

        return (int(p1) * 256) + int(p2)

    def toggle_data_conn_type(self, conn_type):
        '''toggle_data_conn_type(conn_type)
        Toggle the data connection type to be used.'''

        # PASV
        if conn_type == PASV:
            if self.use_pasv:
                System.display('PASV already enabled.')
            else:
                self.use_pasv = True
                self.use_epsv = False
                self.use_port = False
                self.use_eprt = False
                System.display('PASV mode On .')
                log('Setting data transfer moe to PASV')

        # EPSV
        elif conn_type == EPSV:
            if self.use_epsv:
                System.display('EPSV already enabled.')
            else:
                self.use_pasv = False
                self.use_epsv = True
                self.use_port = False
                self.use_eprt = False
                System.display('EPSV mode On .')
                log('Setting data transfer moe to EPSV')

        # PORT
        elif conn_type == PORT:
            if self.use_port:
                System.display('PORT already enabled.')
            else:
                self.use_pasv = False
                self.use_epsv = False
                self.use_port = True
                self.use_eprt = False
                System.display('PORT mode On .')
                log('Setting data transfer moe to PORT')

        # EPRT
        elif conn_type == EPRT:
            if self.use_eprt:
                System.display('EPRT already enabled.')
            else:
                self.use_pasv = False
                self.use_epsv = False
                self.use_port = False
                self.use_eprt = True
                System.display('EPRT mode On .')
                log('Setting data transfer moe to EPRT')

    def toggle_verbose(self):
        '''toggle_verbose()
        Toggle verbose mode on or off. When verbose mode is turned on, then
        server responses are displayed to the console upon retreval.'''

        # Verbose mode Off .
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
REMOTE_HELP = 'remotehelp'

PASV = 'pasv'
EPSV = 'epsv'
PORT = 'port'
EPRT = 'eprt'

HELP = 'help'
QUIT = 'quit'

VERBOSE = 'verbose'

CONN_REQUIRED_COMMANDS = [CWD, PWD, LIST, RETR, STOR, SYST, REMOTE_HELP]
COMMANDS_THAT_USE_DATA_CONN = [LIST, RETR, STOR]
DATA_CONN_COMMANDS = [PASV, EPSV, PORT, EPRT]
USER_COMMANDS = [CWD, PWD, LIST, RETR, STOR, SYST, HELP,
                 REMOTE_HELP, QUIT, VERBOSE, PASV, EPSV, PORT, EPRT]


class DataConnection:

    def __init__(self):
        self.listening_sock = None
        self.conn = None
        self.addr = None
        self.port = None
        self.connected = threading.Event()

    def close(self):
        '''close()
        Close the data connection.'''

        if self.conn:
            try:
                self.conn.close()
                log('Closed data connection.')
            except:
                pass

        if self.listening_sock:
            try:
                self.listening_sock.close()
            except:
                pass

    def connect(self, host, port, addr_fam):
        '''connect()
        Connect data connection to host and set the connected event.'''

        # Connect to server.
        self.conn = socket.socket(addr_fam, socket.SOCK_STREAM)
        self.conn.connect((host, port))

        # Set connected event.
        self.connected.set()
        log(f'Connecting data channel to {host}:{port}')

    def bind(self, addr_fam):
        '''bind(add_fam) -> port number
        Find an open port and bind to it.'''

        low = 50000
        high = 60000

        # Loop until found an open port.
        self.listening_sock = socket.socket(addr_fam, socket.SOCK_STREAM)
        while True:
            # Get random port number within low and high.
            port = System.randint(low, high)
            try:
                # Attempt to bind to port.
                self.listening_sock.bind(('', port))
                log(f'Binding data connection to: localhost:{port}.')
                break
            except:
                pass

        return port

    def listen(self):
        '''listen()
        The data connection listens for the server to connect.'''

        self.listening_sock.settimeout(10)
        self.listening_sock.listen(1)
        try:
            # Accept server data connection.
            try:
                conn, addr = self.listening_sock.accept()
            except socket.timeout:
                return

            # Set attributes.
            self.conn = conn
            self.addr = addr[0]
            self.port = int(addr[1])

            # Set connected event.
            self.connected.set()
            log('Connected to data channel.')
        except KeyboardInterrupt:
            pass

    def receive_data(self, bufsize=4096):
        '''receive_data(bufsize=4096) -> data
        Receive the data transfer from the server.'''

        byte_data = b''
        while True:
            # Receive some data.
            response = self.conn.recv(bufsize)
            byte_data += response

            # Test if end of message.
            if len(response) < bufsize:
                break

        # Decode and log/display to console the data response.
        data = decode(byte_data)
        log(data)
        System.display(data)

        return data

    def send_file(self, path):
        '''send_file(path)
        Send a local file to the server over the data connection.'''

        file_data = System.read_file(path)
        self.conn.sendall(encode(file_data))
        log(f'Sent: "{path}"')



if __name__ == '__main__':
    # Get command line args and initialize logger object..
    # host, filename, port = System.args()
    # host, filename, port = '10.246.251.93', 'mylog.txt', 21
    host, filename, port = '127.0.0.1', 'mylog.txt', 2121
    logger = Logger(filename)

    while True:
        # Connect client to host and begin main processing loop.
        client = Client(host, port)
        try:
            client.connect()
        except KeyboardInterrupt:
            break
        except:
            log("Unable to establish a connection with host.")
            System.display("Unable to establish a connection with host.")
            break

        try:
            main(client, host, port)
        except KeyboardInterrupt as err:
            client.close()
            break
        except Exception as err:
            log(
                f"An error occurred while connected to host, restarting service -> \r\n{err}")
            System.display(
                f"An error occurred while connected to host, restarting service -> \r\n{err}")
