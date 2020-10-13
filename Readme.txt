Edward Parrish

FtpClient uses the latest version of python3.

Usage: python3 ftpclient.py <HOST> <FILENAME> [optional: <PORT>]

    HOST        the host address of the desired FTP server
    FILENAME    the relative path to a log file for recording ftp messages

    optional:
    PORT        the desired port number to connect to the FTP server (default: 21)


Once the program is running, you can use the "help" command to have a list of 
commands displayed. The available commands are described below:

    cd          CHANGE WORKING DIRECTORY
    get         RETRIEVE FILE
    help        DISPLAY HELP MENU
    ls          LIST DIRECTORY
    put         STORE FILE
    pwd         PRINT WORKING DIRECTORY
    quit        QUIT

Issues:
    - the FTP client cannot successfully establish a data connection to a
      server. this renders the commands get, cd, ls, & put useless. Attempting 
      these commands does not have any effect.