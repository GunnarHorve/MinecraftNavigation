#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Queue
from collections import defaultdict
import math

class PriorityQueue:
	def __init__(self):
		self.pq = Queue.PriorityQueue()

	def push(self, object, priority):
		self.pq.put((priority, object))

	def pop(self):
		return self.pq.get()[1]

	def empty(self):
		return self.pq.empty()

class Node:
	def __init__(self, pos, g, f, par, dir):
		self.pos = pos		# (i,j,k) index
		self.g = g			# movement cost
		self.f = f			# movement + heuristic cost
		self.par = par		# parent pointer
		self.dir = dir		# (xDir, yDir, zDir) tuple. (how parent arrived)

	def expand(self, data): 		#27 neighbor expansion
		nodes = []
		for x in range(-1,1):
			for y in range(-1,1):
				for z in range(-1,1):
					pos = (self.pos[0] + x, self.pos[1] + y, self.pos[2] + z)

					if(outOfBounds(pos, data)): continue			#out of bounds
					if(data[pos[0]][pos[1]][pos[2]] == 0): continue #invalid move

					g   = self.g + euclidian(self.pos, pos)
					f   = g + manhattan(pos, endPos)
					par = self
					dir = (x,y,z)
					nodes.append(Node(pos, g, f, par, dir))
		return nodes

def search(startPos, endPos, data):
	pq = PriorityQueue()
	visited = defaultdict(lambda: False)

	n = Node(startPos, 0, manhattan(startPos, endPos), None, None)
	while(n.pos is not endPos):
		if(visited[n.pos]): 	# check if already visited
			continue
		visited[n.pos] = True

		for child in n.expand(data):
			pq.push(child, child.f)

		if pq.empty(): return	# give up and go home
		n = pq.pop() 			# get next node

	return buildPath(n)

##### Helper Methods #####
def buildPath(n):
	path = []
	while(n.parent):
		path.append(n.dir)
		n = n.par

def outOfBounds(pos, data):
	t1 = pos[0] < 0
	t2 = pos[1] < 0
	t3 = pos[2] < 0
	t4 = pos[0] >= len(data)
	t5 = pos[1] >= len(data[0])
	t6 = pos[2] >= len(data[0][0])
	return t1 and t2 and t3 and t4 and t5 and t6

def manhattan(p1, p2):
	return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) + abs(p1[2] - p2[2])

def euclidian(p1, p2):
	return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)
