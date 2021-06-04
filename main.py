# TODO put name and student id before submitting
import csv
from model.package import Package
from model.destination import Destination
from model.truck import Truck
# from controller.deliver import deliver
import model.destination
import controller.hashing_with_chaining
import controller.graph
from math import ceil
import random
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
from datetime import datetime, date, timedelta  # TODO okayy maybe don't use a time format and just % it myself?
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
            graph_instance.add_vertex(vertex, address)
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
                if place[i] != '':
                    vertex_a = graph_instance.get_vertex(graph_instance.vertex_key_list[index_counter])
                    vertex_b = graph_instance.get_vertex(graph_instance.vertex_key_list[i - 2])
                    distance = float(place[i])
                    graph_instance.add_undirected_edge(vertex_a, vertex_b, distance)

                i += 1

            index_counter += 1


# Steps to write the algo and set everything up:
# TODO first implement req following w/ greedy, then 2-opt swaps, then multiple trucks, then annealing??
# Move optimization algos to their own optimization controller file?? maybe just make main.py have create_trucks and
# user interface methods and that's it? everything else in another file, separated as needed
def load_trucks(num_of_trucks, num_packages):  # Nearest Neighbor Algorithm TODO make each truck have <= 16 packages
    # TODO change to just create_trucks() or something and pass the created and optimized lists into this.
    #       create a create_route() method to call before that will return the optimized list and pass that into here.
    first_routes = unoptimized_route(num_packages)
    package_list = two_opt(first_routes)  # TODO after testing for two_opts change to simulated annealing and test vars.
    delayed_packages = []
    delayed_time = None
    route = 1
    truck = None
    for i in range(0, num_of_trucks):  # TODO needs rework for when using more than 1 truck.
        start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        truck = Truck(i+1, package_list[i], start_time, route)
    return truck


# If route is routes[1], then time leaving hub is 9:05... and routes[2] leaves after routes[0]??
# Create list of delayed packages, if one is in the route, then route cannot leave until 9:05.
# make sure truck 2 specified packages are always on package 2 and cannot leave.
# then rearrange vertices to make their deadline. Check all packages in route against their deadline to see if correct.
def unoptimized_route(num_packages):  # Creates pre-optimized route by placing all packages in list in order given.
    start = ' HUB'
    start_location = graph_instance.get_vertex(start)
    num_routes = ceil(num_packages / 16)
    package_list = [[] for _ in range(num_routes)]
    vertex_list = [[start_location] for _ in range(num_routes)]

    for i in range(0, num_routes):  # Create specified number of package_list lists
        for j in range(i*15, (i*15)+15):  # Each truck can only hold 16 packages. Add <= 16 packages to each list.
            if j <= num_packages-1:  # When total # of packages is exhausted, break from loop.
                package_list[i].append(j+1)
                # destination_vertex = None  # If using this, need to get vertex by searching from packages address.
                vertex_list[i].append(graph_instance.get_vertex(j+1))
            else:
                break
        print(len(package_list[i]))

    for sublist in vertex_list:  # Return to hub
        sublist.append(start_location)

    return vertex_list, package_list


def two_opt(input_lists):  # TODO whenever swapping indices in vertex_list, must also swap same indices in package_list.
    #                             remember vertex_list > package_list by 2, because hub is at beginning and end!
    vertex_list = input_lists[0]  # TODO do i even need this??????????????????????????????????????
    package_list = input_lists[1]
    # print(len(vertex_list))
    # print(len(package_list))

    # for i in range(len(vertex_list)):
    #     print(input_lists[0][i])
    #     pass
    return package_list


def simulate_annealing(initial_route):
    route = initial_route  # lol okay.
    temp = .8  # Initial Temperature set to 80°
    target_temp = .01
    cooling_factor = 0.995

    inner_itr = 6000  # variable for num of iterations for exploiting local search area Paper sets this as 6000,overkill
    k = 25  # variable for calculating acceptance probability TODO might not need k! test different variables for best

    while temp > target_temp:
        for i in range(inner_itr):
            # Total distance of route
            d1 = route.get_distance  # ?

            # Produce neighbor of route as a new solution
            new_route = two_opt(route)

            # Total distance of new_route
            d2 = new_route.get_distance

            # probability formula. Initially, high probability of accepting wrong solutions. As temp decreases,
            #   the probability will decrease and tend toward 0 for worse routes. The algorithm will move
            #   deterministically, only accepting better solutions.
            # source: https://stats.stackexchange.com/questions/453309/what-is-the-relationship-between-metropolis-hastings-and-simulated-annealing
            probability = exp(- ((d2-d1) * k) / (d1 * temp))

            if d2 < d1:
                route = new_route
            elif d2 >= d1 and random() < probability:  # if new_route is worse, accept change with probability
                route = new_route

            temp = temp * cooling_factor

    return route


def deliver(loaded_truck):  # TODO truck still needs to return to hub after all packages are delivered.
    packages_delivered = 0
    for package_id in loaded_truck.package_list:
        package = packages_hash.search(package_id)
        current_location = graph_instance.get_vertex(loaded_truck.location)
        next_location = graph_instance.get_vertex(package.get_address())

        distance = graph_instance.get_distance(current_location, next_location)  # in miles
        seconds_taken = int(distance // (loaded_truck.speed / 3600))
        # minutes_taken = int(distance // (loaded_truck.speed / 60))

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

trucks = load_trucks(3, 40)  # TODO each truck only holds 16 packages, 2 drivers. so one driver will need to return to
#                                   hub to change trucks (or reload with remaining packages, doesn't need to change
#                                   trucks necessarily, b/c load times are instantaneous.

deliver(trucks)

from math import exp

print(exp(- (20.0-5) / (40 * .80)))
