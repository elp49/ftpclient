# FtpClient

## Usage:
    python3 ftpclient.py [HOST] [FILENAME] [PORT]

    HOST        the host address of the desired FTP server
    FILENAME    the relative path to a log file for recording ftp messages
    PORT        the desired port number to connect to the FTP server
                port argument is optional and the default is 21

## Commands
Once the program is running, you can use the "help" command to have a list of 
commands displayed. The available commands are described below:

    cd          CHANGE WORKING DIRECTORY
    get         RETRIEVE FILE
    help        DISPLAY HELP MENU
    ls          LIST DIRECTORY
    put         STORE FILE
    pwd         PRINT WORKING DIRECTORY
    quit        QUIT

## Issues:
- The FTP client does not successfully establish a data connection to a server. This renders the get, cd, ls, and put commands useless. Attempting these commands does not have any effect.