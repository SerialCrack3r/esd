# Copyright (c) 2009 Moxie Marlinspike
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#

#import time

import os
import configparser
import binascii
import stat

from random import randint
from struct import *

from Libs.CryptoEngine import CryptoEngine

class Profile:

    def __init__(self, cipherKey="RegbQ1a6pgSDT5tr", macKey="9WUrbn5ARHoQZKn8", counter=0, knockPort=None):
        portSet = [5010, 5011, 5012, 5013, 5014, 5015, 5016, 5017, 5018, 5019, 5020]
        self.counterFile  = None
        self.cipherKey = binascii.a2b_base64(cipherKey)
        self.macKey    = binascii.a2b_base64(macKey)
        self.counter   = counter
        self.knockPort = portSet[randint(0, len(portSet)-1)]    #randomly pick a port to knock to
        self.cryptoEngine = CryptoEngine(self, self.cipherKey, self.macKey, self.counter)

        # New fields
        self.storedCipherKey = ""
        self.storedMacKey = ""
        self.storedCounter = ""


    # Getters And Setters

    def getIPAddrs(self):
        return self.ipAddressList

    def setIPAddrs(self, ipAddressList):
        self.ipAddressList = ipAddressList        

    def getName(self):
        return "test"

    def getDirectory(self):
        return None

    def getKnockPort(self):
        return self.knockPort

    def setCounter(self, counter):
        self.counter = counter

        # The counter appears not to be encrypted so we can directly
        # save it to the "storedCounter" field
        self.storedCounter = self.counter

    # Encrypt And Decrypt

    def decrypt(self, ciphertext, windowSize):
        return self.cryptoEngine.decrypt(ciphertext, windowSize)

    def encrypt(self, plaintext):
        return self.cryptoEngine.encrypt(plaintext)

    # Serialization Methods

    def loadCipherKey(self):
        self.cipherKey = self.storedCipherKey
        return self.cipherKey

    def loadMacKey(self):
        self.macKey = self.storedMacKey
        return self.macKey

    def loadCounter(self):
        self.counter = self.storedCounter
        return int(self.counter)

    def loadConfig(self):
        return None

    def loadKey(self, key):
        return binascii.a2b_base64(key)

    def storeCipherKey(self):
        self.storedCipherKey = self.cipherKey
        # self.storeKey(self.cipherKey, self.directory + "/cipher.key")

    def storeMacKey(self):
        self.storedMacKey = self.macKey
        # self.storeKey(self.macKey, self.directory + "/mac.key")

    def storeCounter(self):
        # Privsep bullshit...
        self.storedCounter = self.counter

    def storeConfig(self):
        # config = configparser.ConfigParser()
        # config.add_section('main')
        # config.set('main', 'knock_port', str(self.knockPort))
        #
        # configFile = open(self.directory + "/config", 'w')
        # config.write(configFile)
        # configFile.close()
        #
        # self.setPermissions(self.directory + "/config")
        return None

    def storeKey(self, key, path):
        # file = open(path, 'w')
        # file.write(binascii.b2a_base64(key))
        # file.close()
        #
        # self.setPermissions(path)
        return None

    # Permissions

    def setPermissions(self, path):
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)

    # Debug

    def printHex(self, val):
        for c in val:
            print("%#x" % ord(c)),
            
        print("")
