from controller.hashing_with_chaining import ChainingHashTable


class Vertex:
    def __init__(self, label):
        self.label = label

    def __str__(self):
        return "%s" % self.label


class Graph:
    def __init__(self):
        self.edge_weights = ChainingHashTable()
        self.vertex_hash = ChainingHashTable()
        self.vertex_key_list = []  # Vertex keys are their addresses.

    def add_vertex(self, new_vertex, address):
        self.vertex_hash.insert(new_vertex, address)  # new
        self.vertex_key_list.append(address)

    def add_directed_edge(self, from_vertex, to_vertex, weight=1.0):
        self.edge_weights.insert(weight, (from_vertex, to_vertex))

    def add_undirected_edge(self, vertex_a, vertex_b, weight=1.0):
        self.add_directed_edge(vertex_a, vertex_b, weight)
        self.add_directed_edge(vertex_b, vertex_a, weight)

    def get_vertex(self, address):
        return self.vertex_hash.search(address)

    def get_distance(self, current_vertex, next_vertex):
        return self.edge_weights.search((current_vertex, next_vertex))

    # def __str__(self):
    #   return "adjList = %s, && edge weights = %s" % (self.adjacency_list, self.edge_weights)
