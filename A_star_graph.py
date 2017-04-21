#!/usr/bin/env python

import Queue
from collections import defaultdict
import math
import time

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
    def __init__(self, index, g, f, par):
        self.index = index  # index of kd tree
        self.g = g			# movement cost
        self.f = f			# movement + heuristic cost
        self.par = par		# parent pointer

    def expand(self, tree, endIndex, expansionFactor):
        nodes = []

        distances, indexes = tree.query(tree.data[self.index], expansionFactor)
        for i in range(expansionFactor):
            index = indexes[i]
            g     = self.g + distances[i]
            f     = g + manhattan(tree.data[index], tree.data[endIndex])
            par = self
            nodes.append(Node(index, g, f, par))

        return nodes

def search(startPos, endPos, tree, expansionFactor):
    pq = PriorityQueue()
    visited = defaultdict(lambda: False)

    _, startIndex = tree.query(startPos)
    _, endIndex   = tree.query(endPos)

    n = Node(startIndex, 0, manhattan(tree.data[startIndex], tree.data[endIndex]), None)
    pq.push(n, n.f)
    while(n.index != endIndex):
        if pq.empty(): return           # give up and go home
        n = pq.pop()                    # get next node

        if(visited[n.index]): continue  # check if already visited
        visited[n.index] = True

        for child in n.expand(tree, endIndex, expansionFactor):
            pq.push(child, child.f)

    return buildWaypoints(startIndex, endIndex, n, tree)

##### Helper Methods #####
def buildWaypoints(startIndex, endIndex, n, tree):
    waypoints = []
    while(n.par):
        waypoints.insert(0, tree.data[n.index])
        n = n.par

    waypoints.insert(0, tree.data[startIndex])
    waypoints.append(tree.data[endIndex])
    return waypoints

def manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) + abs(p1[2] - p2[2])