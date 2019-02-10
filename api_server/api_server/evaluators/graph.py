from collections import namedtuple
import heapq
import math
from typing import Dict, List

Edge = namedtuple('Edge', 'start end weight')
HeapItem = namedtuple('HeapItem', 'dist neighbour')

class Node:
    def __init__(self, weight=1):
        self.weight = weight
        self.neighbours = {} # id:weight

class Station:
    def __init__(self, anode, bnode, adist, bdist):
        assert math.isclose(adist+bdist, 1.0), "%f+%f==%f != 1.0" % (adist, bdist, adist+bdist)

        self.anode = anode # id
        self.bnode = bnode # id
        self.adist = adist # not normalized to edge length!
        self.bdist = bdist

class Graph:
    def __init__(self, nodes: Dict[str, Node], edges: List[Edge]=None):
        self.nodes = nodes
        if edges is not None:
            self.add_all_edges(edges)

    def add_all_edges(self, edges: List[Edge]):
        for start, end, weight in edges:
            self.nodes[start].neighbours[end] = weight
            self.nodes[end].neighbours[start] = weight

    def dijkstra(self, stations: List[Station]):
        for node in self.nodes.values():
            node.dijkstra_mark = 0
            node.dist = math.inf

        heap = []
        for s in stations:
            weight = self.nodes[s.anode].neighbours[s.bnode]
            heap.append(HeapItem(weight*s.adist, s.anode))
            heap.append(HeapItem(weight*s.bdist, s.bnode))

        heapq.heapify(heap)

        while heap:
            dist, id = heap[0]
            heapq.heappop(heap)
            node = self.nodes[id]
            if node.dijkstra_mark == 0:
                node.dijkstra_mark = 1
                node.dist = dist
                for nid, ndist in node.neighbours.items():
                    heapq.heappush(heap, HeapItem(dist+ndist, nid))

def avg(items) -> float:
    return sum(items) / len(items)

def error(graph, stations) -> float:
    graph.dijkstra(stations)
    return avg([node.dist for node in graph.nodes.values()])
