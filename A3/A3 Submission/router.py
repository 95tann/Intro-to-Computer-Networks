#!/usr/bin/env python

# ******************************************************************************************
#  CS 456    : Computer Networks
#  assignment: 3
#  filename  : router.py
#  author    : Tanmay Shah
# ******************************************************************************************

import os, sys, logging
from packet import *
from socket import *

routerSocket = socket(AF_INET, SOCK_DGRAM)

# print error message and exit
def error_msg(msg):
	print("Error: %s" % msg)
	exit()

# begin logging
def start_logging(file,routerID):
	logging.basicConfig()
	log = logging.getLogger(routerID)
	log.setLevel(logging.INFO)
	FileHandler = logging.FileHandler(file)
	FileHandler.setLevel(logging.INFO)
	log.addHandler(FileHandler)
	return log

# logs info for packets
def log_info(routerID, pkt_type, is_send, pkt,log):
	if is_send:
		if pkt_type == "INIT":
			log.info("R" + routerID + " " + "sends an INIT: router_id " + routerID)
		if pkt_type == "HELLO":
			log.info("R" + routerID + " " + "sends a HELLO: router_id " + str(pkt.routerID) + " link_id " + str(pkt.link))
		if pkt_type == "LSPDU":
			log.info("R" + routerID + " " + "sends a LSPDU: sender " + str(pkt.sender) + " router_id " + str(pkt.routerID) + " link_id " + str(pkt.link) +  " via " + str(pkt.via) + " with cost= " + str(pkt.cost))
	else:
		if pkt_type == "HELLO":
			log.info("R" + routerID + " " + "receives a HELLO: router_id " + str(pkt[1].routerID) + " link_id " + str(pkt[1].linkID))
		if pkt_type == "LSPDU":
			log.info("R" + str(routerID) + " " + "receives a LSPDU: sender " + str(pkt[1].sender) + " router_id " + str(pkt[1].routerID) + " link_id " + str(pkt[1].link) + " via " + str(pkt[1].via) + " with cost= " + str(pkt[1].cost))


# verifies and fetches command line input
def fetch_input():
	if (5 != len(sys.argv)):
		error_msg("Invalid no. of parameters entered")

	try:
		routerID = int(sys.argv[1])
		routerPort = int(sys.argv[4])
		emulatorPort = int(sys.argv[3])
		emulatorHost = str(sys.argv[2])
	except:
		error_msg("Invalid types used for parameters")

	return (routerID,routerPort,emulatorPort, emulatorHost)		

def unpack_HELLO(data):
	pkt = struct.unpack("<II", data)
	hello_pkt = pkt_HELLO(pkt[0], pkt[1])
	unpacked = ("HELLO", hello_pkt)
	return unpacked

def unpack_LSPDU(data):
	pkt = struct.unpack("<IIIII", data)
	lspdu_pkt = pkt_LSPDU(pkt[0], pkt[1], pkt[2], pkt[3], pkt[4])
	unpacked = ("LSPDU", lspdu_pkt)
	return unpacked

def send_INIT(routerID, emulatorHost, emulatorPort,log):
	pkt = pkt_INIT(routerID)
	log_info(str(routerID),"INIT",1,pkt,log)
	routerSocket.sendto(pkt.package(), (emulatorHost,emulatorPort))

def send_HELLO(routerID, cost_list, net, log, emulatorHost, emulatorPort):
	for item in cost_list:
		pkt = pkt_HELLO(routerID, item.linkID)
		net.createLink(item,routerID)
		log_info(str(routerID),"HELLO",1,pkt,log)
		routerSocket.sendto(pkt.package(), (emulatorHost,emulatorPort))

def send_LSPDU(routerID, link_costs, via, emulatorHost, emulatorPort,log):
	for item in link_costs:
		pkt = pkt_LSPDU(routerID, routerID, item.linkID, item.cost, via)
		routerSocket.sendto(pkt.package(), (emulatorHost,emulatorPort))
		log_info(str(routerID), "LSPDU", 1, pkt, log)

# begins running router.py
def main(): 
	routerID, routerPort, emulatorPort, emulatorHost = fetch_input()

	# bind socket to port
	routerSocket.bind(("", routerPort))

	# create file & start log
	log_filename = "router" + str(routerID) + ".log"
	route_log = start_logging(log_filename,str(routerID))

	# sending INIT packet to Emulator
	send_INIT(routerID,emulatorHost,emulatorPort,route_log)

	# Setup network topology 
	net = network(0,routerID)

	# Define Router Info. Base
	RIB = {} 

	ID = 1
	while(ID <= 5):
		if ID != routerID:
			RIB[ID] = ("INF", float("inf"))
		else:
			RIB[ID] = ("Local",0)
		ID += 1

	# Fetch Circuit DB from Emulator
	data, client = routerSocket.recvfrom(4096)
	circ_DB = circuit_DB(data)

	# Log info
	log_str1 =  "R" + str(routerID) + " receives a CIRCUIT_DB: nbr_link " + str(circ_DB.nbr_link) + " with"
	route_log.info(log_str1)
	for item in circ_DB.link_cost_list:
		log_str2 = "  link_id " + str(item.linkID) + " & cost " + str(item.cost) 
		route_log.info(log_str2)

	# Send Hello
	send_HELLO(routerID, circ_DB.link_cost_list, net, route_log, emulatorHost, emulatorPort)

	neighbour_list = []

	# Handle incoming packets based on type
	while(1): #await userinput to break loop
		data, client = routerSocket.recvfrom(4096)

		# Deal with PKT LSPDU
		if len(data) == 20:
			unpacked = unpack_LSPDU(data)
			log_info(routerID, "LSPDU", 0, unpacked, route_log)
			link_cost_instance = (unpacked[1].link, unpacked[1].cost)
			net.createLink(link_cost_instance, unpacked[1].routerID)

		# Deal with PKT HELLO
		if len(data) == 8:
			unpacked = unpack_HELLO(data)
			neighbour_list.append(unpacked[1].routerID)
			
			# log network
			route_log.info(" ") # create whitespace seperation for readability
			route_log.info("Topology DB")
			route_log.info("-----------")
			for key in net.links:
				l = str(key.linkID)
				n = str(net.links[key].connections)
				msg1 =  "R" + str(routerID) + " -> R" + l + " nbr link " + n
				route_log.info(msg1)
				for item in net.links[key].neighbours:
					linkID = str(item[0])
					cost = str(item[1])
					msg2 =  "R" + str(routerID) + " -> R" + l + " link " + linkID + " with cost " + cost
					route_log.info(msg2)
			route_log.info(" ") # create whitespace seperation for readability

			# log Routing Info.
			route_log.info("Routing Info. Base")
			route_log.info("------------------")
			for key, value in RIB.items():
				msg = "R" + str(routerID) + " -> " + "R" + str(key)
				route_log.info(msg)
				if(value[0] == "INF"):
					msg = msg + " -> " + value[0] + ", " + "INF"
					route_log.info(msg)

				elif(value[0] == "Local"):
					msg = msg + " -> " + value[0] + ", " +  str(value[1])
					route_log.info(msg)

				else:
					msg = msg + " -> R" + value[0] + ", " + str(value[1])
					route_log.info(msg)

			route_log.info(" ") # create whitespace seperation for readability
			
			# Send LSPDU
			send_LSPDU(routerID, circ_DB.link_cost_list, unpacked[1].link, emulatorHost, emulatorPort,route_log)

main()