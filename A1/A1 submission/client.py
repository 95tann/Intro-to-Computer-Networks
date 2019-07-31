#!/usr/bin/env python

# ***********************************************************************************
#  CS 456    : Computer Networks
#  assignment: 1
#  filename  : client.py
#  author    : Tanmay Shah
# 
# File Description
# ----------------
# This file implements the client-side process of:
# (1) creating UDP socket to negotiate with server using <server_address> & <n_port>
# (2) sending request code via UDP socket
# (3) receiving from & sending back of TCP <r port> to server via UDP socket
# (4) upon acknowledgement, sending message to server via TCP socket
# (5) receving reversed message from server via TCP socket
# ***********************************************************************************
import sys
from socket import *
 
# Fetches & returns a list of command line arguments used with client.sh
def get_input():
	if((len(sys.argv) == 5) and (sys.argv[4] != '')):
		try:
			udp_server_addr = str(sys.argv[1])
			udp_server_port = int(sys.argv[2])
			reqCode = int(sys.argv[3])
			msg = str(sys.argv[4])
			client_input = [udp_server_addr, udp_server_port, reqCode, msg]
			return client_input
		
		except:
			print("Invalid input: check argument type for client.sh") 
			exit()
	
	else:
		print("Invalid no. of arguments for client.sh")
		exit()

# Negotiate with server for TCP <r_port> via UDP connection
def negotiation(client_input):
	try:
		# setup UDP connection
		udp_client_socket = socket(AF_INET, SOCK_DGRAM)
		
		# send request code to server
		udp_client_socket.sendto(str(client_input[2]).encode(),(client_input[0],client_input[1]))
                                   
               	# receive TCP <r_port> from server via UDP connection 
		tcp_server_port, addr = udp_client_socket.recvfrom(1024)
                       
		# send back TCP <r_port> back to server via UDP connection
		udp_client_socket.sendto(str(tcp_server_port).encode(),(client_input[0],client_input[1]))

		# receive & validate acknowledgement of TCP <r_port> from server via UDP connection
		ack_msg, addr = udp_client_socket.recvfrom(1024)
               	if ("ok" == str(ack_msg.decode())):
    			udp_client_socket.close()
    			return tcp_server_port
    			
   		if ("no" == str(ack_msg.decode())):
   			print("client-side: <r_port> acknowledgement unsuccessful")
           		udp_client_socket.close()
    			exit()
	
	except:
  		print("UDP connection failed with server")
    		exit()
  
# Trasact with server to send message & receive reversed message via TCP connection
def transaction(tcp_server_port, client_input):
	try:
		# setup TCP connection with server & send message
    		tcp_client_socket = socket(AF_INET, SOCK_STREAM)
    		tcp_client_socket.connect((client_input[0],int(tcp_server_port)))
    		tcp_client_socket.send(client_input[3].encode())

        	# receive reversed msessage from server and print it
        	reversed_msg, addr = tcp_client_socket.recvfrom(2048)
        	print("CLIENT_RCV_MSG='" + reversed_msg.decode() + "'")

        	# close TCP connection	
        	tcp_client_socket.close()
	
	except:
    		print("TCP connection failed with server")
     		exit()


# Main function that begins running the client.py code
def run_client():

	# get arguments inputted with client.sh
	client_input = get_input()

	# Stage 1 - Negotiation using UDP sockets
	tcp_server_port = negotiation(client_input)
    	
    	# Stage 2 - Transaction using TCP sockets
    	transaction(tcp_server_port,client_input)
   

# begin running client.py
run_client()