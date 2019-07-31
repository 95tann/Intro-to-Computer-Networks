# *************************************************************
#  CS 456    : Computer Networks
#  Assignment: 3
#  Filename  : README.txt
#  Author    : Tanmay Shah
# *************************************************************

Summary
-------
The files in this assignment are used to implement shortest path routing (OSPF). The relevant files for this assignment include:
1) router.py 
2) packet.py
3) nselinux386 (emulator)

Note that there is no Makefile since all implementation is done using Python3

Execution Instructions
----------------------
1) To run emulator, enter the following command in bash: ./nse-linux386 <routerHost> <emaularPort> (i.e. ./nse-linux386 129.97.167.27 9998)
2) To run 1 of 5 routers, enter the following command in bash: python router.py <routerID> <emulatorHost> <emulatorPort> <routerPort> (i.e. python router.py 2 129.97.167.26 9998 5444)


Argument Specifications
-----------------------
Emulator:
1) <routerHost>   : server address of host where router.py is running
2) <emulatorPort> : port number that Emulator is listening for messsages

Router:
1) <routerID>     : ID of currently running router (ID between 1 & 5)
2) <emulatorHost> : server address of host where Emulator is running
3) <emulatorPort> : port number that Emulator is listening for messages
4) <routerPort>   : port number used by router for communication

Testing
-------
This assignment was tested on different UWaterloo Linux student environment machines: 
1) 5 instances of router.py were rendered on ubuntu1604-008
2) Emulator was rendered on ubuntu1604-006 

