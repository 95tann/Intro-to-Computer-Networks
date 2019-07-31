#!/usr/bin/env python

# ******************************************************************************************
#  CS 456    : Computer Networks
#  assignment: 3
#  filename  : packet.py
#  author    : Tanmay Shah
# ******************************************************************************************

import struct 

# code below is used to define a bunch of classes that will be used by router
class node:
	def __init__(self, link, num, dest_router):
		self.neighbours = {} # dictionary with linkID as keys, (dest_router, link.cost) as value
		self.connections = num

	def modify(self, link, dest_router):
		self.modified = 0

		# link not in dict (neighbours)
		if link.linkID not in self.neighbours:
			self.neighbours[link.linkID] = (dest_router, link.cost)
			self.modified = 1
			self.connections = self.connections + 1

		# link in dict (neighbours) but different destination
		for key, value in self.neighbours.items():
			if ((link.cost == value[1]) and (dest_router != value[0]) and (key == link.linkID)):
				self.modified = 1
				self.neighbours[key] = (dest_router, link.cost)

class pkt_LSPDU:
	def __init__(self, sender, routerID, link, cost, via):
		self.routerID = routerID
		self.cost = cost
		self.link = link
		self.via = via
		self.sender = sender

	def package(self):
		package = struct.pack("<IIIII", self.sender, self.routerID, self.link, self.cost, self.via)
		return package

class network:
	def __init__(self, change, routerID):
		self.modified = change
		self.routerID = routerID
		self.links = {} # dictionary of network links

	def handle_dest(self, link, routerID, dest):
		if (dest not in [0,-1]):
			if (self.modified == 1):
				modify_node = self.links[dest]
				modify_node.modify(link,routerID)

	def createLink(self, link, routerID):
		self.modified = 0

		# get destination router
		dest = 0
		for router_node in self.links:
			if router_node == routerID:
				dest = -1
			else:
				dest = -1 
				for key in self.links[router_node].neighbours:
					if link.linkID == key:
						dest = router_node
						break

		if routerID not in self.links:
			self.modified = 1       
			self.links[link] = node(link, 1, dest) # add to links dictionary

		if routerID in self.links:
			to_modify = self.links[routerID]
			self.modified = to_modify.modify(link, dest)

		self.handle_dest(link, routerID, dest)

class pkt_HELLO:
	def __init__(self, routerID, link):
		self.link = link
		self.routerID = routerID

	def package(self):
		package = struct.pack("<II", self.routerID, self.link)
		return package

class pkt_INIT:
	def __init__(self, routerID):
		self.routerID = routerID

	def package(self):
		package = struct.pack("<I", self.routerID)
		return package

class link_cost:
	def __init__(self, link, cost):
		self.linkID = link
		self.cost = cost

class circuit_DB: 
	def __init__(self, info):
		self.link_cost_list = []
		self.unpack(info)

	def unpack(self,info):
		self.nbr_link = struct.unpack_from("<I", info, 0)[0]
		r = 0
		while (r < self.nbr_link):
			ofst = 4 + (8*r)
			parsed_info = struct.unpack_from("<II", info, ofst)
			parsed_link = link_cost(parsed_info[0],parsed_info[1])
			self.link_cost_list.append(parsed_link)
			r += 1