#!/usr/bin/env python

# ******************************************************************************************
#  CS 456    : Computer Networks
#  assignment: 1
#  filename  : server.py
#  author    : Tanmay Shah
# 
# File Description
# ----------------
# This file implements the server-side process of:
# (1) creating UDP socket <n_port> for negotiation with the client
# (2) receving & verifying request code sent by client via UDP socket
# (3) upon verification, creating a TCP <r_port> 
# (4) sending TCP <r_port> to client via UDP socket
# (5) receiving <r_port> sent by client & sending acknowledgement via UDP socket
# (6) receving client message and sending back reversed message to client via TCP socket
# *****************************************************************************************
import sys
from socket import *

# Fetches and returns <request code> from command line input
def get_reqcode():

    if (len(sys.argv) == 2):
        try:
            reqCode = int(sys.argv[1]) 
            return reqCode
        except:
            print("Invalid input: argument type for server.sh must be an integer") 
            exit()
    else:
        print("Invalid no. of arguments for server.sh")
        exit()


# Reverses the input text
def reverse(text):
    reversed = text[::-1]
    return reversed


# Negotiate with client to establish TCP <r_port> and return TCP socket/port
def negotiation(udp_server_socket, request_code):

    is_negotiation_complete = False

    while(is_negotiation_complete == False):

        # get request code from client via UDP connection
        request_code_recv, client_addr = udp_server_socket.recvfrom(1024)
        
        # request code received is valid
        if (str(request_code) == str(request_code_recv)): 
                  
            # create TCP socket for server
            tcp_server_socket = socket(AF_INET,SOCK_STREAM)
            tcp_server_socket.bind(('',0))
            tcp_server_socket.listen(1)

            # generate & send TCP <r_port> to client via UDP connection
            random_port = tcp_server_socket.getsockname()[1]       
            encoded_port = str(random_port).encode()           
            udp_server_socket.sendto(encoded_port,client_addr) 

            # fetch TCP <r_port> received by client is correct
            r_port_client, client_addr = udp_server_socket.recvfrom(1024)
                
            # TCP <r_port> doesn't match
            if (str(r_port_client.decode()) != str(random_port)):
                print("server-side: incorrect <r_port> received by client")
                ack_msg = "no"
                udp_server_socket.sendto(ack_msg.encode(), client_addr) 
                     
            # TCP <r_port> matches
	    else:
                ack_msg = "ok"
                udp_server_socket.sendto(ack_msg.encode(), client_addr)
                is_negotiation_complete = True

        # invalid request code received
        else: 
            print("Invalid request code: expected %s, but received %s" % (str(request_code),str(request_code_recv)))

         
    return (tcp_server_socket, r_port_client)


# Transact with client to receive message & send reversed message
def transaction(tcp_server_socket, r_port_client):

    # accept client messages on TCP socket
    tcp_connection, addr = tcp_server_socket.accept()
          
    # listen and print TCP <r_port> & client messsage
    client_msg = tcp_connection.recv(2048)  
    print("SERVER_TCP_PORT=" + str(r_port_client))
    print("SERVER_RCV_MSG='" + client_msg.decode() + "'") 

    # respond to client by sending back reversed message
    reversed_msg = reverse(client_msg.decode())                
    tcp_connection.send(str(reversed_msg).encode())     
                     
    # close TCP socket connection
    tcp_connection.close()


# Main function that begins running the server.py code
def run_server():

    # get request code that server is expecting
    request_code = get_reqcode()   
    
    try:
        # fetch & print first available UDP <n port> to negotiate 
        udp_server_socket = socket(AF_INET,SOCK_DGRAM)
        udp_server_socket.bind(('',0))
        
        # print negotiation port
        negotiation_port = udp_server_socket.getsockname()[1]       
        print("SERVER_PORT=" + str(negotiation_port))

        while(1):
            # Stage 1 - Negotiation
            tcp_server_socket, r_port_client = negotiation(udp_server_socket, request_code)

            # Stage 2 - Transaction
            transaction(tcp_server_socket, r_port_client)

    except:
        # connection failure
        print("server connection failure")
        exit()


# begin running server.py
run_server() 