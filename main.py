# TODO put name and student id before submitting
import csv
from model.package import Package
from model.truck import Truck
import model.hashing_with_chaining
import model.graph
from controller.unoptimized_route import unoptimized_route
from controller.simulated_annealing import simulated_annealing
from controller.ui import user_menu
from controller.deliver import deliver
from datetime import datetime, date
from pathlib import Path


def load_package_data(input_data, header_lines):  # Move to it's own controller file??
    """
    Parses the csv file and stores the package data in a hash data structure using hashing with chaining.

    Time Complexity: Worst Case O(N^2) if packages_hash puts all packages into the same hash bucket
                     Average Case O(N)
    Space Complexity: O(N)

    :param input_data: csv file containing the package data
    :param header_lines: number of header lines to skip in the csv file
    """
    with open(input_data) as items:
        data = csv.reader(items, delimiter=',')

        for i in range(0, header_lines):
            next(data, None)  # skip specified number of header lines

        for item in data:  # parse data into separate items
            new_id = int(item[0])
            new_address = item[1]
            new_city = item[2]
            new_state = item[3]
            new_zip = item[4]
            if item[5] == 'EOD':  # EOD chosen as 5pm
                new_deadline = datetime.now().replace(hour=17, minute=0, second=0, microsecond=0)
            else:  # parse into datetime time
                new_time = datetime.strptime(item[5], "%I:%M %p").time()
                new_deadline = datetime.combine(date.today(), new_time)
            new_mass = item[6]
            if item[7] == '':
                new_notes = ''
            else:
                new_notes = item[7]

            # create item object
            new_item = Package(new_id, new_address, new_city, new_state, new_zip, new_deadline, new_mass, new_notes)
            # print(new_item)

            packages_hash.insert(new_item, new_id)
            # print(hash_instance_packages.search(new_id))


def load_destination_data(input_data, header_lines):  # Move to own controller file??
    """
    Parses the csv file and stores the destination and distances data in a graph data structure.

    Time Complexity: Worst Case O(N^2) if graph_instance.add_vertex, graph_instance.get_vertex, or
                                        graph_instance.add_undirected_edge places into a hash that
                                        puts all elements into the same bucket.
                     Average Case O(N)
    Space Complexity: O(N)

    :param input_data: csv file containing the destination and distances data
    :param header_lines: number of header lines to skip in the csv file
    """
    with open(input_data) as places:
        data = csv.reader(places, delimiter=',')
        num_col = len(next(data))  # count number of columns in the csv file
        places.seek(0)  # Return csv reader back to start of file
        for i in range(0, header_lines):  # skip specified number of header lines
            next(data, None)

        for place in data:  # Add all vertices to the graph.
            address = place[1]
            vertex = model.graph.Vertex(address)
            graph_instance.add_vertex(vertex, address)

        places.seek(0)  # Return csv reader back to start of file.
        for i in range(0, header_lines):  # skip specified number of header lines
            next(data, None)

        index_counter = 0
        for place in data:  # Add edges to the graph.
            # name = place[0]
            # key = place[1]
            i = 2
            while place[i] != '':
                if place[i] != '':
                    vertex_a = graph_instance.get_vertex(graph_instance.vertex_key_list[index_counter])
                    vertex_b = graph_instance.get_vertex(graph_instance.vertex_key_list[i - 2])
                    distance = float(place[i])
                    graph_instance.add_undirected_edge(vertex_a, vertex_b, distance)
                i += 1
                if i > num_col - 1:
                    break

            index_counter += 1


def load_trucks(optimized_routes):
    """
    Creates each truck object

    Time Complexity: O(1)
    Space Complexity: O(1)

    :param optimized_routes: The list of routes (lists with package id's in optimized order)
    :return: list of all loaded trucks
    """

    truck = []
    for i in range(0, 3):  # Create the 3 trucks and include the optimized package lists
        start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        truck.append(Truck(i + 1, optimized_routes[i], start_time))
    return truck


# Starts counter of how long the program takes to complete optimization process
runtime = datetime.now()

# paths to the csv files
data_path = Path("data/WGUPS Package File.csv")
data_path_destination = Path("data/WGUPS Distance Table.csv")

# initialize the ChainingHashTable instance
packages_hash = model.hashing_with_chaining.ChainingHashTable()

# initialize the Graph instance. Input set as n^2, where n = the number of destinations in 'WGUPS Distance Table.csv' to
#   reduce collisions and keep lookup time as close to O(1) as possible.
graph_instance = model.graph.Graph(729)

# load the package and destination data into their respective data structures.
load_package_data(data_path, 8)
load_destination_data(data_path_destination, 8)

# create an initial route
first_routes = unoptimized_route(packages_hash, 40)
# optimize the route
routes = simulated_annealing(packages_hash, graph_instance, first_routes)

# create truck objects and load them with the optimized delivery routes
trucks = load_trucks(routes)
# simulate the delivery of the trucks and process time and mileage to complete the deliveries
deliver(packages_hash, graph_instance, trucks)

print('Optimization Runtime: ', end='')
print(datetime.now()-runtime)

# start the console menu
user_menu(packages_hash)
