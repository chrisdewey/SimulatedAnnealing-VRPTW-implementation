from model.hashing_with_chaining import ChainingHashTable


class Vertex:
    def __init__(self, label):
        """
        Creates a vertex with the given label.

        Time Complexity: O(1)
        Space Complexity: O(1)

        :param label: The name of the vertex
        """
        self.label = label

    def __str__(self):
        return "%s" % self.label


class Graph:
    def __init__(self, num_edge_weights=100):
        """
        Initializes the Graph and its associated hash tables and key list.

        Time Complexity: O(1)
        Space Complexity: O(N) where N = the number of buckets in the hash tables

        :param num_edge_weights: Optional parameter, the number of edge weights to initialize the edge_weights hash with
        """
        self.edge_weights = ChainingHashTable(num_edge_weights)
        self.vertex_hash = ChainingHashTable()
        self.vertex_key_list = []  # Vertex keys are their addresses.

    def add_vertex(self, new_vertex, key):
        """
        Adds a vertex to the graph
        
        Time Complexity: Worst Case O(N) if all items hash to the same bucket in the vertex_hash
                         Average Case O(1)
        Space Complexity: O(N)
        
        :param new_vertex: The object to be inserted
        :param key: 
        """
        self.vertex_hash.insert(new_vertex, key)
        self.vertex_key_list.append(key)

    def add_directed_edge(self, from_vertex, to_vertex, weight=1.0):
        """
        Adds a directed edge to the edge_weights hash table.

        Time Complexity: Worst Case O(N) if all items hash to the same bucket in the edge_weights hash table
                         Average Case O(1)
        Space Complexity: O(N)

        :param from_vertex: Vertex the edge leaves from
        :param to_vertex: Vertex the edge gos to
        :param weight: Weight of the edge
        """
        self.edge_weights.insert(weight, (from_vertex, to_vertex))

    def add_undirected_edge(self, vertex_a, vertex_b, weight=1.0):
        """
        Adds an undirected edge by calling add_directed_edge in both directions.

        Time Complexity: Worst Case O(N) if all items hash to the same bucket in the edge_weights hash table
                         Average Case O(1)
        Space Complexity: O(N)

        :param vertex_a:
        :param vertex_b:
        :param weight:
        """
        self.add_directed_edge(vertex_a, vertex_b, weight)
        self.add_directed_edge(vertex_b, vertex_a, weight)

    def get_vertex(self, key):
        """
        Using the key, returns the graph vertex from the vertex_hash.

        Time Complexity: Worst Case O(N) if all items hash to the same bucket in the vertex_hash
                         Average Case O(1)
        Space Complexity: O(1)

        :param key:
        :return: The vertex from the graph (stored in the vertex_hash)
        """
        return self.vertex_hash.search(key)

    def get_distance(self, current_vertex, next_vertex):
        """
        Returns the edge weight between the two input vertices using the edge_weights hash table.

        Time Complexity: Worst Case O(N) if all items hash to the same bucket in the edge_weights hash table
                         Average Case O(1)
        Space Complexity: O(1)

        :param current_vertex:
        :param next_vertex:
        :return: edge weight between the two vertices
        """
        return self.edge_weights.search((current_vertex, next_vertex))
