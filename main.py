# TODO put name and student id before submitting
import csv
from model.package import Package
from model.destination import Destination
from model.truck import Truck
# from controller.deliver import deliver
import model.destination
import controller.hashing_with_chaining
import controller.graph
from datetime import time, timedelta
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
from datetime import datetime, time, date, timedelta  # TODO okayy maybe don't use a time format and just % it myself?
from pathlib import Path
# from operator import attrgetter  -> this is for getting the attribute. can get attribute of a list of model and
#       sort by the specific attribute (like distance from hub etc)??


def user_search():  # will need to adapt to allow input of time as well?? implement after figuring out algo i guess.
    #   Maybe just print out a list of all packages and their statuses at the user-inputted time specified. Read sec. G

    #   after calculating routes, user enters specified time and recalculate package/truck positions and times to show
    #       store end_time for after all trucks finish their route? use this if they specify later time, return complete

    # From Reddit: Implement a way, given a time and/or a package id
    # default being all packages, to meet the checkpoint screenshot requirements)

    # Input asks for either HH:MM am/pm or 24hr clock???? would just have to check and parse.
    search_id = input('Enter the package ID for lookup, or type Exit to exit: ')

    exit_words = ['exit', 'x', 'close', 'bye', 'end']
    if search_id.lower() in exit_words:
        print('Goodbye.')
        return

    try:
        search_id = int(search_id)
        item = packages_hash.search(search_id)
        if item is not None:
            print(item)
            user_search()
        else:
            print('Could not Find Package: ' + str(search_id))
            user_search()
    except ValueError:
        print('Could Not Find Package: ' + search_id)
        user_search()


def load_package_data(input_data, header_lines):  # Move to it's own controller file??
    """Parses the csv file and stores the package data in a hash data structure using hashing with chaining."""
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
                new_notes = None
            else:
                new_notes = item[7]

            # create item object
            new_item = Package(new_id, new_address, new_city, new_state, new_zip, new_deadline, new_mass, new_notes)
            # print(new_item)

            packages_hash.insert(new_item, new_id)
            # print(hash_instance_packages.search(new_id))


def load_destination_data(input_data, header_lines):  # Move to own controller file??
    """Parses the csv file and stores the destination data in a graph data structure."""
    with open(input_data) as places:
        data = csv.reader(places, delimiter=',')
        num_col = len(next(data))  # count number of columns in the csv file
        places.seek(0)  # Return csv reader back to start of file
        for i in range(0, header_lines):  # skip specified number of header lines
            next(data, None)

        for place in data:  # Add all vertices to the graph.
            address = place[1]
            vertex = controller.graph.Vertex(address)
            graph_instance.add_vertex(vertex)
            # print(vertex)

        places.seek(0)  # Return csv reader back to start of file.
        for i in range(0, header_lines):  # skip specified number of header lines
            next(data, None)

        index_counter = 0
        for place in data:  # Add edges to the graph.
            name = place[0]
            address = place[1]
            i = 2
            while place[i] != '' and i < num_col-1:
                # print(graph_instance.adjacency_list[address])
                if place[i] != '':
                    # vertex_a = keys_list[index_counter]
                    # vertex_b = keys_list[i-2]
                    vertex_a = graph_instance.vertex_list[index_counter]
                    vertex_b = graph_instance.vertex_list[i-2]
                    distance = float(place[i])
                    graph_instance.add_undirected_edge(vertex_a, vertex_b, distance)
                    # with add_undirected_edge it gives 28 members to each vertex, with directed, it gives 1 then 2
                    #   then 3 etc.. also the last vertex is missing its last connection, b/c there's an index out of
                    #   bounds error stemming from num_col-1 i believe...

                i += 1

            index_counter += 1


# Steps to write the algo and set everything up:
# TODO first implement req following w/ greedy, then 2-opt swaps, then multiple trucks, then annealing??
# Move optimization algos to their own optimization controller file?? maybe just make main.py have create_trucks and
# user interface methods and that's it? everything else in another file, separated as needed
def load_trucks(num_of_trucks, num_packages):  # Nearest Neighbor Algorithm TODO make each truck have <= 16 packages
    first_routes = nearest_neighbor(num_packages)  # List may only have a max index of 15, then check for times? & org.
    package_list = two_opt(first_routes)
    delayed_packages = []
    delayed_time = None
    route = 1
    truck = None
    for i in range(0, num_of_trucks):  # TODO needs rework for when using more than 1 truck.
        start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        truck = Truck(i+1, package_list, start_time, route)
    return truck


# If route is routes[1], then time leaving hub is 9:05...
# Create list of delayed packages, if one is in the route, then route cannot leave until 9:05.
# make sure truck 2 specified packages are always on package 2 and cannot leave.
# then rearrange vertices to make their deadline. Check all packages in route against their deadline to see if correct.
def unoptimized_tour(num_packages):  # Creates pre-optimized route by placing all packages in list in order given.
    package_list = []

    start = ' HUB'
    start_location = graph_instance.get_vertex(start)

    vertex_list = [start_location]

    for i in range(1, num_packages+1):
        package_list.append(packages_hash.search(i))
        vertex_list.append(graph_instance.get_vertex(i))

    vertex_list.append(start_location)  # Return to hub

    return vertex_list, package_list


def nearest_neighbor(num_packages):  # TODO possibly take out and just use random/original order as first tour,
    #                                       depending on how efficient either method is in comparison.
    unvisited_locations = []
    package_list = []
    for i in range(1, num_packages+1):  # add all packages to unvisited_locations list
        unvisited_locations.append(i)

    start = ' HUB'
    current_location = graph_instance.get_vertex(start)
    vertex_list = [current_location]
    tour_distance = 0.0
    # TODO for optimizing using req.s: after truck lists are set, if the truck has any packages req to be after 9:00
    #   or a specific time, hold the truck until after that time. That way the packages can be sent out in the most
    #   optimized way possible, while still being after the specified time?

    # TODO when implementing 2-opt swaps: First save the tour using vertices in a list, not the packages,
    #   Do the swaps until optimized, then convert the tour into the optimize-ordered package list for each truck.
    #   For swaps: must not swap tour[0] -> being the HUB.
    #   Will need to also add distance calculator in this method, not just saved to trucks.
    # Less than O(N^2) time? b/c list is decreasing w/ each iteration... ask StackOverflow?
    while unvisited_locations:  # While unvisited_locations list is not empty:
        closest_package = packages_hash.search(unvisited_locations[0])  # Initialize with first package on list
        closest_neighbor = graph_instance.get_vertex(closest_package.get_address())
        closest_neighbor_distance = 0.0
        for i in range(1, num_packages + 1):
            if i not in unvisited_locations:
                continue
            package = packages_hash.search(i)
            package_location = graph_instance.get_vertex(package.get_address())

            # if package_location == current_location:  # not sure if i need this???????????????????
            #   break

            package_distance = graph_instance.get_distance(current_location, package_location)
            closest_neighbor_distance = graph_instance.get_distance(current_location, closest_neighbor)

            if package_distance < closest_neighbor_distance:
                closest_neighbor = package_location
                closest_package = package

        tour_distance += closest_neighbor_distance
        current_location = closest_neighbor
        vertex_list.append(closest_neighbor)
        package_list.append(closest_package)
        # print(tour_distance)
        # print(current_location, closest_neighbor)
        # print(closest_package)
        # print()

        unvisited_locations.remove(closest_package.id_)

    vertex_list.append(graph_instance.get_vertex(start))  # truck returns to HUB at EOD
    tour_distance += (graph_instance.get_distance(vertex_list[-2], vertex_list[-1]))  # add distance back to hub
    # print(tour_distance)
    return vertex_list, package_list


def two_opt(input_lists):  # TODO whenever swapping indices in vertex_list, must also swap same indices in package_list.
    #                             remember vertex_list > package_list by 2, because hub is at beginning and end!
    vertex_list = input_lists[0]
    package_list = input_lists[1]
    # print(len(vertex_list))
    # print(len(package_list))
    for i in range(len(vertex_list)):
        # print(input_lists[0][i])
        pass
    return package_list


def simulated_annealing(input_list):
    pass


def deliver(loaded_truck):  # TODO truck still needs to return to hub after all packages are delivered.
    packages_delivered = 0
    for package in loaded_truck.packages:
        current_location = graph_instance.get_vertex(loaded_truck.location)
        next_location = graph_instance.get_vertex(package.get_address())

        distance = graph_instance.get_distance(current_location, next_location)  # in miles
        seconds_taken = int(distance // (loaded_truck.speed / 3600))
        minutes_taken = int(distance // (loaded_truck.speed / 60))

        loaded_truck.time += timedelta(seconds=seconds_taken)
        # print()
        # print(distance)
        # print(seconds_taken)
        # print(minutes_taken)
        # loaded_truck.time = time_string_forward(loaded_truck.time, minutes_taken)

        loaded_truck.miles_traveled += distance

        # after delivering package, current truck location is the just delivered packages address.
        loaded_truck.location = package.get_address()

        packages_delivered += 1
    #  Next 7 lines used just for returning to hub.. matches a lot of other lines. TODO Make separate function??
    start = ' HUB'
    hub = graph_instance.get_vertex(start)
    distance = graph_instance.get_distance(graph_instance.get_vertex(loaded_truck.location), hub)
    minutes_taken = int(distance // (loaded_truck.speed / 60))

    # loaded_truck.time = time_string_forward(loaded_truck.time, minutes_taken)

    loaded_truck.miles_traveled += distance
    loaded_truck.location = start
    # return_to_hub =
    print(loaded_truck.miles_traveled)
    print(packages_delivered)
    print(loaded_truck.time)


# paths to the csv files
data_path = Path("data/WGUPS Package File.csv")
data_path_destination = Path("data/WGUPS Distance Table.csv")

# initialize the ChainingHashTable instance
packages_hash = controller.hashing_with_chaining.ChainingHashTable()
# initialize the Graph instance
graph_instance = controller.graph.Graph()

# second argument = the number of header lines to skip in the csv file before processing the data.
load_package_data(data_path, 8)
load_destination_data(data_path_destination, 8)

# user_search()

trucks = load_trucks(1, 40)  # TODO each truck only holds 16 packages, 2 drivers. so one driver will need to return to
#                                   hub to change trucks (or reload with remaining packages, doesn't need to change
#                                   trucks necessarily, b/c load times are instantaneous.

deliver(trucks)
