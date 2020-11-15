Edward Parrish

FtpClient uses the latest version of python3.


Usage:
    python3 ftpclient.py [-v] host filename [port]

    -v          Suppresses display of server responses.
    host        Specifies the host address of the FTP server to connnect to.
    filename    Specifies the file to write sent and received FTP messages.
    port        Specifies the port number for the FTP server (default: 21).


Once the client is started, it will immediately attempt to connect to the host
machine specified by its host address in the command line on the specified port
(or default port 21 is none is given). The "help" command lists the available
commands:

    cd          CHANGE WORKING DIRECTORY
    get         RETRIEVE FILE
    help        DISPLAY HELP MENU
    ls          LIST DIRECTORY
    put         STORE FILE
    pwd         PRINT WORKING DIRECTORY
    quit        QUIT


Issues:
 - The FTP client does not successfully establish a data connection to a server.
 This renders the get, cd, ls, and put commands useless. Attempting these
 commands does not have any effect.


Testing:
    This code has been tested locally using a Debian-derived Linux distribution
    application on Windows 10 OS as well as on Drexel's tux machine.
