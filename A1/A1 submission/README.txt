# *************************************************************
#  CS 456    : Computer Networks
#  assignment: 1
#  filename  : README.txt
#  author    : Tanmay
# *************************************************************

Summary
-------
The files in this assignment are used to implement communication between a client and a server using UDP & TCP connections. In particular, the client sends a message to the server and receives a reversed version of the message back from the server. The relevant files for this assignment include:
1) server.sh
2) client.sh
3) server.py
4) client.py

Note that there is no Makefile since all implementation is done using Python


Execution Instructions
----------------------
1) To run server code, enter the following command in bash: ./server.sh <req_code> (i.e. ./server.sh 11) 
2) To run client code, enter the following command in bash: ./client.sh <server_addr> <n_port> <req_code> <msg> (i.e. ./client.sh 129.97.167.27 52500 11 'Hello World')


Argument Specifications
-----------------------
1) <server_addr> : The server address must match the address of the server that is currently running
2) <msg>         : The message must be a non-empty string 
3) <n_port>      : This is the negotiated port that is printed once server begins running
4) <req_code>    : The request code inputted must be of type integer. Futhermore, this request code must be identical for both server.sh & client.sh


Testing
-------
This assignment was tested on on UWaterloo Linux student environment (ubuntu1604-008). The following test was sucessfully run:
bash command: ./server.sh 50
bash command: ./client.sh 129.97.167.27 57854 50 'Computer Networks'

server output:
SERVER_PORT=57854
SERVER_TCP_PORT=41438
SERVER_RCV_MSG='Computer Networks'

client output:
CLIENT_RCV_MSG='skrowteN retupmoC'
