class Vertex:
    def __init__(self, label):
        self.label = label

    def __str__(self):
        return "%s" % self.label


class Graph:
    def __init__(self):
        self.adjacency_list = {}
        self.edge_weights = {}

    def add_vertex(self, new_vertex):
        self.adjacency_list[new_vertex] = []

    def add_directed_edge(self, from_vertex, to_vertex, weight=1.0):
        self.edge_weights[(from_vertex, to_vertex)] = weight
        self.adjacency_list[from_vertex].append(to_vertex)

    def add_undirected_edge(self, vertex_a, vertex_b, weight=1.0):
        self.add_directed_edge(vertex_a, vertex_b, weight)
        self.add_directed_edge(vertex_b, vertex_a, weight)

    # def __str__(self):
    #   return "adjList = %s, && edge weights = %s" % (self.adjacency_list, self.edge_weights)

# https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value     see here, might want to
# sort dictionary by distance values and replace into an ordered dict, must be careful about ordering the vertex
# names correctly.
