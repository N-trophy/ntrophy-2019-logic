import heapq
import math

#!/usr/bin/env python3

"""
N-trophy 2019 logic task score evaluator for graphs.

This sripts accepts input as a single multiline file.
Format: each line contains one point.
 * 'C id x y' -- define city at [x, y]
 * 'S id_a id_b x y' -- define ambulace station at [x, y] that belongs to the road from city id_a to id_b
 * 'R' id_a id_b -- define road from city id_a to id_b
Usage: graph_evaluator input.txt
Output: single number representing error (lower = better, optimum = 0)
Error = average distance of each city to the nearest station
"""

class Node:
    def __init__(self):
        self.neighbours = []
        self.pos = (0, 0)
        self.dijkstra_mark = 0
        self.dist = math.inf
        self.id = 0

class Graph:
    def __init__(self, size):
        self.nodes = [Node() for _ in range(size)]
        for i in range(size):
            self.nodes[i].id = i

    def edge_length(a, b):
        dx = a.pos[0] - b.pos[0]
        dy = a.pos[1] - b.pos[1]
        return math.sqrt(dx**2 + dy**2)
    
    def add_node(self, id, pos):
        self.nodes[id].pos = pos
    
    def add_edge(self, id_a, id_b):
        self.nodes[id_a].neighbours.append(id_b)
        self.nodes[id_b].neighbours.append(id_a)
    
    def dijkstra(self, initial_set):
        for node in self.nodes:
            node.dijkstra_mark = 0
            node.dist = math.inf

        heap = initial_set
        heapq.heapify(heap)
        while len(heap):
            dist, id = heap[0]
            heapq.heappop(heap)
            node = self.nodes[id]
            if node.dijkstra_mark == 0:
                node.dijkstra_mark = 1
                node.dist = dist
                for neighbour_id in node.neighbours:
                    newdist = dist + Graph.edge_length(node, self.nodes[neighbour_id])
                    heapq.heappush(heap, (newdist, neighbour_id))

    def print_dist(self):
        for node in self.nodes:
            print("{}: {}".format(node.id, node.dist))


def load_from_file(file_name):
    n = 0
    g = Graph(n)
    initial_set = []
    with open(file_name) as input_file:
        for line in input_file:
            data = list(map(lambda x: x.strip(), line.split(" ")))
            if data[0] == 'SIZE':
                g = Graph(int(data[1]))
            if data[0] == 'N':
                id = int(data[1])
                x = int(data[2])
                y = int(data[3])
                g.add_node(id, (x, y))
            if data[0] == 'E':
                id_a = int(data[1])
                id_b = int(data[2])
                g.add_edge(id_a, id_b)
            if data[0] == 'S':
                id_a = int(data[1])
                id_b = int(data[2])
                x = float(data[3])
                y = float(data[4])
                dist_a = math.sqrt((g.nodes[id_a].pos[0]-x)**2 + (g.nodes[id_a].pos[1]-y)**2)
                dist_b = math.sqrt((g.nodes[id_b].pos[0]-x)**2 + (g.nodes[id_b].pos[1]-y)**2)
                initial_set.append((dist_a, id_a))
                initial_set.append((dist_b, id_b))
    g.dijkstra(initial_set)
    return g

g = load_from_file("graph.txt")
error = sum(list(map(lambda node: node.dist, g.nodes))) / len(g.nodes)
print("Error: {}".format(error))
g.print_dist()