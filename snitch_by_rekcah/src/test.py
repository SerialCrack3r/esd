#!/usr/bin/env python

# import socket
import sys
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.connect(("8.8.8.8", 80))
# print(s.getsockname())
# s.close()


# Print color codes

W  = '\033[0m'  # white (normal)
R  = '\033[31m' # red
G  = '\033[32m' # green
O  = '\033[33m' # orange
B  = '\033[34m' # blue
P  = '\033[35m' # purple

# End Print color codes


def prompt(message = ""):
    client_id = 2
    if message == "" :
        if client_id <= 0:
            sys.stdout.write(">> Your command : ")
        else:
            sys.stdout.write("[ " + str(client_id) + " ] >> Your command : ")
    else :
        sys.stdout.write(message)

    sys.stdout.flush()

def parse_command():
    client_id = 2
    client_count = 3

    cmd = input(">.test")
    if cmd.upper() == "HELP" :
        print("display help")
    elif cmd.upper() == "LIST" :
        print("list clients")
    elif cmd.upper() == "EXIT":
        if input(R + "/!\ Are you sure you want to exit the C&C ? /!\ ? yes/no" + W).upper() == "YES":
            print("exit all")
    else :
        # Parsing commands with arguments
        sub = cmd.split(" ")    # Split the command by the space caracter and parse it
        if sub[0].upper() == "SEL" :
            if 0 < int(sub[1]) <= client_count :
                client_id = int(sub[1]);
                print(G + "[+] Selected client id is now %d" % client_id + W)
            else :
                print(R + "[-] There is no client matching the id you've entered" + W)
        elif sub[0].upper() == "GETINFO" :
            if client_id <= 0 :
                print(R + "[-] You need to select a client to use this command" + W)
            else :
                print(sub[0])    # send "getinfo" to the client and expect it's return
        elif sub[0].upper() == "SHELL" :
            if client_id <= 0 :
                print(R + "[-] You need to select a client to use this command" + W)
            else :
                print(cmd)    #send the command alone tho the client and expect the response
        elif sub[0].upper() == "KILL" :
            if client_id <= 0:
                print(R + "[-] You need to select a client to use this command" + W)
            else:
                print(sub[0])  # send "kill" to the client and expect the response
        elif sub[0].upper() == "REMOVE" :
            if client_id <= 0:
                print(R + "[-] You need to select a client to use this command" + W)
            else:
                print(sub[0])  # send "remove" to the client and expect the response
        elif sub[0].upper() == "GETFILE" :
            if client_id <= 0:
                print(R + "[-] You need to select a client to use this command" + W)
            else:
                print(cmd)  # send "kill" to the client and expect the response

while 1 :
    prompt()
    parse_command()







print(1)
# Get the list sockets which are readable with 'select'
read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])
for sock in read_sockets:
    # new connection
    if sock == server_socket:
        # Handle the case in which there is a new connection recieved through server_socket
        sockfd, addr = server_socket.accept()
        CONNECTION_LIST.append(sockfd)
        client_count += 1
        print(B + "[*] Client (%s, %s) connected" % addr + W)
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
                broadcast_data(sock, "\r" + '<' + str(sock.getpeername()) + '> ' + data)
        except:
            broadcast_data(sock, "Client (%s, %s) is offline" % addr + W)
            print(R + "[-] Client (%s, %s) is offline" % addr + W)
            sock.close()
            CONNECTION_LIST.remove(sock)
            continue