# *************************************************************
#  CS 456    : Computer Networks
#  assignment: 2
#  filename  : README.txt
#  author    : Tanmay
# *************************************************************

Summary
-------
The files in this assignment are used to implement Go-Back-N procol between two hosts (sender and receiver) via a network emulator.
The relevant files for this assignment include:
1) Makefile
2) sender.java
3) receiver.java
4) packet.java*
5) nEmulator-linux386
6) sample.txt (file used as parameter for Sender)

*This file has been modified (maxDataLength & SeqNumModulo have been changed from private to public constants)


Compilation Instructions
------------------------
To compile the files and render the executables, simply enter the 'make' command in terminal


Sample Execution Instructions
-----------------------------
1) To run Emulator : ./nEmulator-linux386 5871 129.97.167.26 4234 6888 129.97.167.27 4502 1 0.1 1
2) To run Receiver : java receiver 129.97.167.46 6888 4234 'output.txt'
3) To run Sender   : java sender 129.97.167.46 5871 4502 'sample.txt'



Parameter Specifications
------------------------
Sender:
- <host address of the network emulator>
- <UDP port number used by the emulator to receive data from the sender>
- <UDP port number used by the sender to receive ACKs from the emulator>
- <name of the file to be transferred>

Receiver:
- <hostname for the network emulator> 
- <UDP port number used by the link emulator to receive ACKs from the receiver>
- <UDP port number used by the receiver to receive data from the emulator>
- <name of the file into which the received data is written>

Emulator:
- <emulator's receiving UDP port number in the forward (sender) direction>
- <receiver’s network address>
- <receiver’s receiving UDP port number>
- <emulator's receiving UDP port number in the backward (receiver) direction>
- <sender’s network address>
- <sender’s receiving UDP port number>
- <maximum delay of the link in units of millisecond>
- <packet discard probability>
- <verbose-mode>


Testing
-------
This assignment was tested on the following UWaterloo Linux student environments 
- Emulator: ubuntu1604-002
- Sender  : ubuntu1604-008
- Receiver: ubuntu1604-006
