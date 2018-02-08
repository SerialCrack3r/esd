#!/usr/bin/env python

__author__   = "rekcah"
__email__    = "rekcah@keabyte.com"
__desc__     = "For educational purposes only ;)"

from struct import *
import time, os, sys
import getopt
import subprocess
from src.core.Profile import Profile

# Shell Colors
W = '\033[0m'  # white (normal)
R = '\033[31m'  # red
G = '\033[32m'  # green
O = '\033[33m'  # orange
B = '\033[34m'  # blue
P = '\033[35m'  # purple
# End Shell colors

class knocker:

    def __init__(self, server, port):
        self.port = port
        self.server = server


    def checkPermissions(self):
        if os.getuid() != 0:
            print("Sorry, you must be root to run this.")
            sys.exit(2)

    def knock(self):
        self.checkPermissions()
        profile = self.getProfile(self.server)
        port = pack('!H', int(self.port))
        packetData = profile.encrypt(port)
        knockPort = profile.getKnockPort()

        (idField, seqField, ackField, winField) = unpack('!HIIH', packetData)

        hping = self.existsInPath("hping3")

        if hping is None:
            print("Error, you must install hping3 first.")
            sys.exit(2)

        command = [hping, "-S", "-c", "1",
               "-p", str(knockPort),
               "-N", str(idField),
               "-w", str(winField),
               "-M", str(seqField),
               "-L", str(ackField),
               self.server]

        try:
            subprocess.call(command, shell=False, stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT)
            print('Knock sent.')

        except OSError:
            print("Error: Do you have hping3 installed?")
            sys.exit(3)

    def usage(self):
        print("Usage: knockknock.py -p <portToOpen> <host>")
        sys.exit(2)

    def parseArguments(self, argv):
        try:
            port = 0
            host = ""
            opts, args = getopt.getopt(argv, "h:p:")

            for opt, arg in opts:
                if opt in ("-p"):
                    port = arg
                else:
                    self.usage()

            if len(args) != 1:
                self.usage()
            else:
                host = args[0]

        except getopt.GetoptError:
            self.usage()

        if port == 0 or host == "":
            self.usage()

        return (port, host)

    def getProfile(self, host):
        homedir = os.path.expanduser('~')

        if not os.path.isdir(homedir + '/.knockknock/'):
            print("Error: you need to setup your profiles in " + homedir + '/.knockknock/')
            sys.exit(2)

        if not os.path.isdir(homedir + '/.knockknock/' + host):
            print('Error: profile for host ' + host + ' not found at ' + homedir + '/.knockknock/' + host)
            sys.exit(2)

        return Profile(homedir + '/.knockknock/' + host)


    def existsInPath(self, command):
        def isExe(fpath):
            return os.path.exists(fpath) and os.access(fpath, os.X_OK)

        for path in os.environ["PATH"].split(os.pathsep):
            exeFile = os.path.join(path, command)
            if isExe(exeFile):
                return exeFile

        return None
