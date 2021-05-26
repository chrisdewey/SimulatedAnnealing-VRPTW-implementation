# Christian Dewey, Student ID: #000957010
import csv
from model.item_to_deliver import Package
from model.destination import Destination
from model.truck import Truck
from controller.deliver import deliver
import model.destination
import controller.hashing_with_chaining
import controller.graph
# it might be better to use hashing with chaining rather than open-addressing... depends how pythons hash() works
#   and how the data is imported and hashed out (like what key is used??)
# from controller.load_item_data import load_items

# Load Trucks, which packages go into which truck, what time do they leave
# Truck Routes
# For UI: user passes in the Time, outputs statuses of Mileage, package statuses & info (is it in hub, delivered? etc)
# UI can just be a console application

# ideas for optimizing:
#   you can hold a truck until 9, need to optimize miles NOT time.
#   maybe use a priority queue, first a normal queue for mile optimization, then introduce priorities based
#       upon special requests like time requirements etc????
#   https://www.youtube.com/watch?v=SC5CX8drAtU watch this for ideas on optimization
#   https://youtu.be/v5kaDxG5w30?t=588 also this at this time
#   might want to change hash function to a different type, maybe reference textbook. save optimization like this
#       for after the functionality is complete.

from pathlib import Path
# from operator import attrgetter  -> this is for getting the attribute. can get attribute of a list of model and
#       sort by the specific attribute (like distance from hub etc)??


def user_search():  # will need to adapt to allow input of time as well?? implement after figuring out algo i guess.
    search_id = input('Enter the package ID for lookup, or type Exit to exit: ')

    exit_words = ['exit', 'x', 'close', 'bye', 'end']
    if search_id.lower() in exit_words:
        print('Goodbye.')
        return

    try:
        search_id = int(search_id)
        item = hash_instance_packages.search(search_id)
        if item is not None:
            print(item)
            user_search()
        else:
            print('Could not Find Package: ' + str(search_id))
            user_search()
    except ValueError:
        print('Could Not Find Package: ' + search_id)
        user_search()


def load_items(input_data, header_lines):
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
            new_deadline = item[5]
            new_mass = item[6]
            if item[7] == '':
                new_notes = None
            else:
                new_notes = item[7]

            # create item object
            new_item = Package(new_id, new_address, new_city, new_state, new_zip, new_deadline, new_mass, new_notes)

            hash_instance_packages.insert(new_item, new_id)
            # print(hash_instance_packages.search(new_id))


def load_destinations(input_data, header_lines):
    with open(input_data) as places:
        data = csv.reader(places, delimiter=',')
        num_col = len(next(data))  # Number of columns in the csv file,
        for i in range(0, header_lines-1):  # TODO: if there is no header lines, then ^ this skips the first element
            next(data, None)  # skip specified number of header lines

        place_num = 0

        for place in data:  # Add all vertices to the graph.
            address = place[1]
            vertex = controller.graph.Vertex(address)
            graph_instance.add_vertex(vertex)
            # print("okay")

        places.seek(0)  # Return csv reader back to start of file.
        for i in range(0, header_lines):  # TODO Okayyyyyy i'm not following what's happening here. don't know why it's
            #                               TODO not the same as the one above, header_lines-1 includes an unwanted row.
            #                               TODO but i'm not quite sure where to place the places.seek() 0 or 1????
            next(data, None)  # skip specified number of header lines

        index_counter = 0
        keys_list = list(graph_instance.adjacency_list)
#        print(keys_list)

        for place in data:  # Add edges to the graph.
            name = place[0]
            address = place[1]
            i = 2

            while place[i] != '' and i < num_col-1:
                # print(graph_instance.adjacency_list[address])
                if place[i] != '':
                    vertex_a = keys_list[index_counter]
                    # print(vertex_a)
                    vertex_b = keys_list[i-2]
                    # print(vertex_b)
                    distance = float(place[i])
                    graph_instance.add_directed_edge(vertex_a, vertex_b, distance)
                    # TODO with add_undirected_edge it gives 28 members to each vertex, with directed, it gives 1 then 2
                    # TODO then 3 etc.. also the last vertex is missing its last connection, b/c there's an index out of
                    # TODO bounds error stemming from num_col-1 i believe...
                # print(place[i])
                i += 1

            index_counter += 1
            # new_place = Destination(place_num, name, address, distances

            # graph_instance.add_undirected_edge()

            # could instead loop though csv for every lookup, but this could be very slow/??
            # Or, and hear me out here -> if the destination[] list is longer, then it's closer to the bottom of the
            # csv file anyway, so just compare their len() and the one with the longer one is daddy. papa.
            place_num += 1  # increment place_num for use as id/index
            # print(hash_instance_destinations.search(address))
            # print()


def load_trucks(num_of_trucks):
    package_list = []
    for i in range(1, 41):  # TODO: make dynamic
        package_list.append(i)
    route = 1
    truck = None
    for i in range(1, num_of_trucks+1):
        truck = Truck(i, package_list, route)
    return truck


def deliver():
    # print(trucks.location)
    for package in trucks.packages:
        # print(hash_instance_packages.search(package))
        # TODO: access packages destination address' distance from current location
        # print()
        pass


# path to the csv file
data_path = Path("data/WGUPS Package File.csv")
data_path_destination = Path("data/WGUPS Distance Table.csv")

# initialize the ChainingHashTable instance
hash_instance_packages = controller.hashing_with_chaining.ChainingHashTable()
# hash_instance_destinations = controller.hashing_with_chaining.ChainingHashTable()
graph_instance = controller.graph.Graph()


load_items(data_path, 8)  # second argument = the number of header lines to skip before processing the data.
load_destinations(data_path_destination, 8)

# keys_list = list(graph_instance.adjacency_list)
# key = keys_list[0]
# print(key)
# for k, v in graph_instance.adjacency_list.items():
#     print(k, v)

# print(graph_instance.adjacency_list[key])


# user_search()

trucks = load_trucks(1)
deliver()
