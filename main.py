# TODO put name and student id before submitting
import csv
from model.package import Package
from model.truck import Truck

import model.hashing_with_chaining
import model.graph
from math import ceil, exp
from random import random, randint, choice
from copy import deepcopy

# For UI: user passes in the Time, outputs statuses of Mileage, package statuses & info (is it in hub, delivered? etc)
# UI can just be a console application

#   https://www.youtube.com/watch?v=SC5CX8drAtU watch this for ideas on optimization
#   https://youtu.be/v5kaDxG5w30?t=588 also this at this time
#   might want to change hash function to a different type, maybe reference textbook. save optimization like this
#       for after the functionality is complete.
from datetime import datetime, date, timedelta
from pathlib import Path
import time


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
                new_notes = ''
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
        # If needed can instead change num_col to header_col to get names of each place in a list as a keys list
        # then num_col can be len() of that var.
        num_col = len(next(data))  # count number of columns in the csv file
        places.seek(0)  # Return csv reader back to start of file
        for i in range(0, header_lines):  # skip specified number of header lines
            next(data, None)

        for place in data:  # Add all vertices to the graph.
            address = place[1]
            vertex = model.graph.Vertex(address)
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


def load_trucks(num_packages):
    first_routes = unoptimized_route(num_packages)
    package_list = simulated_annealing(first_routes)
    route = 1
    truck = []
    for i in range(0, 3):  # Create the 3 trucks and include the optimized package lists
        start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        truck.append(Truck(i+1, package_list[i], start_time, route))
    return truck


def unoptimized_route(num_packages):  # Creates un-optimized routes in which packages still meet their requirements.
    package_id_list = []
    num_routes = ceil(num_packages / 16)  # Create the num of require routes. Each route can have <= 16 packages.
    route_list = [[] for _ in range(num_routes)]
    for i in range(1, num_packages+1):
        package_id_list.append(i)

    end_time = datetime.strptime('5:00 pm', "%I:%M %p").time()  # min deadline, initialize as EOD
    eod = datetime.combine(date.today(), end_time)
    mid_day = datetime.strptime('10:30 am', "%I:%M %p").time()  # min deadline, initialize as EOD
    min_deadline = datetime.combine(date.today(), mid_day)

    for i in package_id_list[:]:  # Distribute condition met packages to specified routes
        package = packages_hash.search(i)

        if package.notes.startswith('Can only be on truck'):  # Specific truck requirement
            route_list[int(package.notes[-1]) - 1].append(i)  # appends to route of specific truck.
            package_id_list.remove(i)
        elif package.notes.startswith('Delayed'):  # Delayed packages requirement
            if package.deadline < eod:  # If the delayed package also has a deadline, prepend to front of list.
                route_list[1].insert(0, i)  # Prepend to list
                package_id_list.remove(i)
            else:
                delayed_until = datetime.strptime(package.notes[-7:], "%I:%M %p").time()  # last 7 last digits = time.
                delayed_until_datetime = datetime.combine(date.today(), delayed_until)  # Needed????
                route_list[1].append(i)
                package_id_list.remove(i)
        elif package.notes.startswith('Wrong address'):
            route_list[2].append(i)
            package_id_list.remove(i)

    for i in package_id_list[:]:  # Distribute packages with deadlines
        package = packages_hash.search(i)

        if package.deadline < min_deadline:  # Distribute packages w earliest deadline
            for j in range(len(route_list)):
                if len(route_list[j]) < 16:  # Compare deadline times so 9:00 deadline is delivered before 10:30 ones???
                    route_list[j].insert(0, i)  # Prepend to the list
                    package_id_list.remove(i)
                    break

        elif package.deadline < eod:  # Distribute other packages w a deadline
            for j in range(len(route_list)):
                if len(route_list[j]) < 16:  # Compare deadline times so 9:00 deadline is delivered before 10:30 ones???
                    route_list[j].insert(1, i)  # Prepend to the list
                    package_id_list.remove(i)
                    break

    for i in package_id_list:  # Assign all other packages to the lists
        for j in range(len(route_list)):
            if len(route_list[j]) < 16:
                route_list[j].append(i)
                break

    return route_list


def valid_move(routes_list, ra_num, rb_num, a, b):
    is_valid = True

    package_a = packages_hash.search(routes_list[ra_num][a])
    package_b = packages_hash.search(routes_list[rb_num][b])

    morning_time = datetime.strptime('9:30 am', "%I:%M %p").time()
    morning = datetime.combine(date.today(), morning_time)
    mid_day_time = datetime.strptime('11:00 am', "%I:%M %p").time()
    mid_day = datetime.combine(date.today(), mid_day_time)

    if package_a.notes.startswith('Can only be'):
        if int(package_a.notes[-1]) != rb_num + 1:  # If package is swapped out of the required truck
            is_valid = False

    if package_b.notes.startswith('Can only be'):
        if int(package_b.notes[-1]) != ra_num + 1:  # If package is swapped out of the required truck
            is_valid = False

    if package_a.deadline < morning:  # Package w morning deadline must be on early leaving routes and near the front
        if rb_num != 0:
            is_valid = False
        if b > 4:
            is_valid = False

    if package_b.deadline < morning:  # Package w morning deadline must be on early leaving routes and near the front
        if ra_num != 0:
            is_valid = False
        if a > 4:
            is_valid = False

    if package_a.deadline < mid_day:
        if rb_num > 1:  # Packages w deadlines must not be one last route
            is_valid = False
        if rb_num == 0 and b > 12:
            is_valid = False
        if rb_num == 1 and b > 6:
            is_valid = False

    if package_b.deadline < mid_day:
        if ra_num > 1:  # Packages w deadlines must not be one last route
            is_valid = False
        if ra_num == 0 and a > 12:
            is_valid = False
        if ra_num == 1 and a > 6:
            is_valid = False

    if package_a.notes.startswith('Must be'):  # Packages delivered together must stay on first route
        if rb_num != 0:
            is_valid = False
    if package_b.notes.startswith('Must be'):  # Packages delivered together must stay on first route
        if ra_num != 0:
            is_valid = False

    return is_valid


def create_new_route(routes_list, distances):
    """
    Swaps a 2 elements within a route, or swaps two elements in separate routes with a 50% chance.
    Requires O(2N) Space  # Worded correctly???????????????

    :param routes_list: The list of routes to be optimized
    :param distances: List of distances for each sub route in routes_list
    :return: new_routes a valid neighbor of routes_list
             new_distances the list of distances of the new_routes list
    """
    new_routes = deepcopy(routes_list)  # Copy of the routes_list
    new_distances = distances.copy()

    if random() < .5:  # Swap 2 elements within the same list. 50% chance
        rn = randint(0, len(new_routes) - 1)

        a = randint(0, len(new_routes[rn]) - 1)  # random element from the list by index
        b = choice([i for i in range(len(new_routes[rn]) - 1) if i != a])  # random element must differ from a

        if valid_move(new_routes, rn, rn, a, b):
            # Swap the two elements
            new_routes[rn][a], new_routes[rn][b] = new_routes[rn][b], new_routes[rn][a]

            # Calculate new distance
            new_distances = update_distances(routes_list, rn, rn, a, b, distances)

    else:  # Swap 2 elements from different lists. 50% chance
        ra_num = randint(0, len(new_routes) - 1)  # Random route a, by index
        rb_num = choice([i for i in range(len(new_routes)-1) if i != ra_num])  # Random route b, must differ from ra_num

        a = randint(0, len(new_routes[ra_num]) - 1)  # random element from ra_num route list, by index
        b = randint(0, len(new_routes[rb_num]) - 1)  # random element from rb_num route list, by index

        if valid_move(new_routes, ra_num, rb_num, a, b):
            # Swap the two elements
            new_routes[ra_num][a], new_routes[rb_num][b] = new_routes[rb_num][b], new_routes[ra_num][a]

            # Calculate new distance
            new_distances = update_distances(routes_list, ra_num, rb_num, a, b, distances)

    return new_routes, new_distances


def simulated_annealing(initial_route):
    routes = initial_route  # List of the routes
    mileage = find_mileages(routes)  # Distances of each sub route in route
    d1 = sum(mileage)  # Total distance of route

    temp = 240  # Initial Temperature set to 80° ?? y decimal and no just 80?? need to test vars!
    target_temp = 0.05
    cooling_factor = 0.995

    inner_itr = 100  # variable for num of iterations for exploiting local search area Paper sets this as 6000,overkill

    while temp > target_temp:
        for i in range(inner_itr):
            neighbor = create_new_route(routes, mileage)
            new_route = neighbor[0]
            new_mileage = neighbor[1]  # Distance of new_route
            # print('og route')
            # print(routes)
            # print('new routes to be considered')
            # print(new_route)
            # print()
            # if not is_valid(new_route):
            #     continue

            d2 = sum(new_mileage)  # Total distance of new_mileage

            # probability formula. Initially, high probability of accepting wrong solutions. As temp decreases,
            #   the probability will decrease and tend toward 0 for worse routes. The algorithm will move
            #   deterministically, only accepting better solutions.
            # source: https://stats.stackexchange.com/questions/453309/what-is-the-relationship-between-metropolis-hastings-and-simulated-annealing
            # TODO in comment here site source as wiki or a paper that has the formula, rather than a forum comment.

            print("Work in progress( 0%%)", end=None)  # Python 2 print without newline
            progress = 0

            # if d2 = d1, then do nothing... TODO or would it be better to make last ELSE be accept, meaning accept if =
            if d2 < d1:
                routes = new_route.copy()
                # print('less')
                # print()
                d1 = d2
                # print()
                # print('                                                       better')
            elif d2 > d1:  # if new_route is not better, accept change with probability
                try:
                    probability = 1 / (exp((d2 - d1) / temp))
                except OverflowError:
                    probability = 0

                if random() < probability:
                    routes = new_route.copy()
                    d1 = d2

        temp = temp * cooling_factor

        if temp:
            progress = None
            print("\b\b\b\b\b%2d%%)" % progress, end=None)

    return routes


def find_mileages(package_lists):
    """
    FUNCTION: find_total_mileage

    DESCRIPTION: Calculates the total mileage a route will take from start to finish. For each route list, the function
    first finds the distance from the HUB to the first packages' address. Then loops through the rest of the packages
    and adds the distance. Finally finds the distance from the final address back to the HUB.

    INPUT: (package_lists)  - A list of all of the package lists (the truck routes)

    OUTPUT: (mileage)       - A list of each routes total mileage to deliver all of the packages in the given order.
    """
    mileage = [0.0 for _ in range(len(package_lists))]
    for i in range(len(package_lists)):
        # Find mileage from HUB to first Address
        package = packages_hash.search(package_lists[i][0])
        hub = graph_instance.get_vertex(' HUB')
        package_address = graph_instance.get_vertex(package.get_address())
        mileage[i] += graph_instance.get_distance(hub, package_address)

        for j in range(len(package_lists[i])-1):
            next_package = packages_hash.search(package_lists[i][j+1])
            next_address = graph_instance.get_vertex(next_package.get_address())

            mileage[i] += graph_instance.get_distance(package_address, next_address)

            package = next_package
            package_address = next_address

        # Find mileage from the last address back to the HUB
        mileage[i] += graph_instance.get_distance(package_address, hub)
        # print('mileage ' + str(i))
        # print(mileage[i])
        # print()
    return mileage


def update_distances(routes_list, route_a, route_b, element_a, element_b, distances):
    """
    Determines the change in the routes distance, taking into account whether either element swapped was
    the first or last package to be delivered in their route.

    :param routes_list:
    :param route_a:
    :param route_b:
    :param element_a:
    :param element_b:
    :param distances:
    :return: The updated list of distances.
    """
    new_d = distances.copy()

    package_a = packages_hash.search(routes_list[route_a][element_a])
    a = graph_instance.get_vertex(package_a.get_address())
    package_b = packages_hash.search(routes_list[route_b][element_b])
    b = graph_instance.get_vertex(package_b.get_address())
    hub = graph_instance.get_vertex(' HUB')

    if element_a == 0:
        prev_a = hub
    else:
        prev_a_package = packages_hash.search(routes_list[route_a][element_a - 1])
        prev_a = graph_instance.get_vertex(prev_a_package.get_address())

    if element_b == 0:
        prev_b = hub
    else:
        prev_b_package = packages_hash.search(routes_list[route_b][element_b - 1])
        prev_b = graph_instance.get_vertex(prev_b_package.get_address())

    if element_a == len(routes_list[route_a])-1:
        next_a = hub
    else:
        next_a_package = packages_hash.search(routes_list[route_a][element_a + 1])
        next_a = graph_instance.get_vertex(next_a_package.get_address())

    if element_b == len(routes_list[route_b])-1:
        next_b = hub
    else:
        next_b_package = packages_hash.search(routes_list[route_b][element_b + 1])
        next_b = graph_instance.get_vertex(next_b_package.get_address())

    if a == prev_b:  # a and b are neighbors, and a comes first
        new_d[route_a] -= graph_instance.get_distance(prev_a, a)
        new_d[route_a] += graph_instance.get_distance(prev_a, b)

        new_d[route_b] -= graph_instance.get_distance(b, next_b)
        new_d[route_b] += graph_instance.get_distance(a, next_b)
    elif b == prev_a:  # a and b are neighbors, and b comes first
        new_d[route_b] -= graph_instance.get_distance(prev_b, b)
        new_d[route_b] += graph_instance.get_distance(prev_b, a)

        new_d[route_a] -= graph_instance.get_distance(a, next_a)
        new_d[route_a] += graph_instance.get_distance(b, next_a)
    else:  # a and b are not neighbors
        new_d[route_a] -= graph_instance.get_distance(prev_a, a)
        new_d[route_a] += graph_instance.get_distance(prev_a, b)

        new_d[route_a] -= graph_instance.get_distance(a, next_a)
        new_d[route_a] += graph_instance.get_distance(b, next_a)

        new_d[route_b] -= graph_instance.get_distance(prev_b, b)
        new_d[route_b] += graph_instance.get_distance(prev_b, a)

        new_d[route_b] -= graph_instance.get_distance(b, next_b)
        new_d[route_b] += graph_instance.get_distance(a, next_b)

    return new_d


def find_total_time(package_lists):
    time_taken = 0
    for route in package_lists:
        # Find mileage from HUB to first Address
        package = packages_hash.search(route[0])
        hub = graph_instance.get_vertex(' HUB')
        package_address = graph_instance.get_vertex(package.get_address())
        time_taken += graph_instance.get_distance(hub, package_address)

        for i in range(len(route)-1):
            next_package = packages_hash.search(route[i+1])
            next_address = graph_instance.get_vertex(next_package.get_address())

            time_taken += graph_instance.get_distance(package_address, next_address)

            package = next_package
            package_address = next_address


def deliver(loaded_truck):
    packages_delivered = 0
    mileage = 0.0
    for i in range(len(loaded_truck)):
        truck = loaded_truck[i]

        if i == 1:  # Truck 2 leaves at 9:05 am for delayed packages
            leave_time = datetime.now().replace(hour=9, minute=5, second=0, microsecond=0)
            truck.time = leave_time
        if i == 2:  # Truck 3 leaves after Truck 1 returns to HUB
            truck.time = loaded_truck[0].time

        for package_id in truck.package_list:
            package = packages_hash.search(package_id)
            # Package w wrong address is updated after 10:30 am. Because it is on Truck 3, it will always be after 10:30
            if package.notes.startswith('Wrong address'):
                package.address ='410 S State St'
                package.city = 'Salt Lake City'
                package.state = 'UT'
                package.zip_ = '84111'
            current_location = graph_instance.get_vertex(truck.location)
            next_location = graph_instance.get_vertex(package.get_address())
            print(package_id)
            distance = graph_instance.get_distance(current_location, next_location)  # in miles
            seconds_taken = int(distance // (truck.speed / 3600))
            print(distance)
            truck.time += timedelta(seconds=seconds_taken)
            package.status = truck.time
            # print()
            # print(distance)
            # print(seconds_taken)
            # print(minutes_taken)
            # loaded_truck.time = time_string_forward(loaded_truck.time, minutes_taken)

            truck.miles_traveled += distance

            # after delivering package, current truck location is the just delivered packages address.
            truck.location = package.get_address()

            packages_delivered += 1
        #  Next 5 lines used just for returning to hub.. matches a lot of other lines. TODO Make separate function??
        start = ' HUB'
        hub = graph_instance.get_vertex(start)
        distance = graph_instance.get_distance(graph_instance.get_vertex(truck.location), hub)
        truck.miles_traveled += distance
        truck.location = start

        mileage += truck.miles_traveled
        print(truck.miles_traveled)
        print(truck.time)
        print(packages_delivered)
        print(truck.package_list)
        print()
    print()
    print('mileage')
    print(mileage)


beginit = datetime.now()
# paths to the csv files
data_path = Path("data/WGUPS Package File.csv")
data_path_destination = Path("data/WGUPS Distance Table.csv")

# initialize the ChainingHashTable instance
packages_hash = model.hashing_with_chaining.ChainingHashTable()

# initialize the Graph instance. Input set as n^2, where n = the number of destinations in 'WGUPS Distance Table.csv' to
#   reduce collisions and keep lookup time as close to O(1) as possible.
graph_instance = model.graph.Graph(729)

# second argument = the number of header lines to skip in the csv file before processing the data.
load_package_data(data_path, 8)
load_destination_data(data_path_destination, 8)

trucks = load_trucks(40)

deliver(trucks)


print()
print('delivered')
print()
for n in range(1, 41):
    print(packages_hash.search(n))
print('time =')
print(datetime.now()-beginit)
# print('Test probability:')
# print(exp(- (20.0-5) / (40 * .80)))

# user_search()
