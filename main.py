# TODO put name and student id before submitting
import csv
from model.package import Package
from model.destination import Destination
from model.truck import Truck
# from controller.deliver import deliver
import model.destination
import controller.hashing_with_chaining
import controller.graph
from math import ceil, exp
from random import random, randint, choice
from copy import deepcopy
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
                new_notes = ''
            else:
                new_notes = item[7]

            # create item object
            new_item = Package(new_id, new_address, new_city, new_state, new_zip, new_deadline, new_mass, new_notes)
            # print(new_item)

            packages_hash.insert(new_item, new_id)
            # print(hash_instance_packages.search(new_id))


def load_destination_data(input_data, header_lines):  # Move to own controller file?? TODO might not need header_lines??
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


# Steps to write the algo and set everything up:
# TODO first implement req following w/ greedy, then 2-opt swaps, then multiple trucks, then annealing??
# Move optimization algos to their own optimization controller file?? maybe just make main.py have create_trucks and
# user interface methods and that's it? everything else in another file, separated as needed
def load_trucks(num_packages):  # Nearest Neighbor Algorithm TODO make each truck have <= 16 packages
    # TODO change to just create_trucks() or something and pass the created and optimized lists into this.
    #       create a create_route() method to call before that will return the optimized list and pass that into here.
    first_routes = unoptimized_route(num_packages)
    package_list = simulated_annealing(first_routes)  # TODO after testing for two_opts change to simulated annealing and test vars.
    route = 1
    truck = []
    for i in range(0, 3):  # Create the 3 trucks and include the optimized package lists
        start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        truck.append(Truck(i+1, package_list[i], start_time, route))
    return truck


# If route is routes[1], then time leaving hub is 9:05... and routes[2] leaves after routes[0]??
# Create list of delayed packages, if one is in the route, then route cannot leave until 9:05.
# make sure truck 2 specified packages are always on package 2 and cannot leave.
# then rearrange vertices to make their deadline. Check all packages in route against their deadline to see if correct.
# TODO Try this, w SA, then test vs trying w a random (just in order) route list before SA and swaps.
# TODO so far this function is NOT completely accurate (places deadline packages out of order in some cases)
# TODO or! put explicit req items in place, then don't worry about time windows until 2swapping?
def unoptimized_route(num_packages):  # Creates un-optimized routes by placing all packages in list in order given.
    earliest_time = None
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
            # implement check if it has a deadline.. not needed for this dataset though.
        elif package.notes.startswith('Delayed'):  # Delayed packages requirement
            if package.deadline < eod:  # If the delayed package also has a deadline, prepend to front of list.
                route_list[1].insert(0, i)  # Prepend to list TODO make choice of route dynamic???
                package_id_list.remove(i)
            else:
                delayed_until = datetime.strptime(package.notes[-7:], "%I:%M %p").time()  # last 7 last digits = time.
                delayed_until_datetime = datetime.combine(date.today(), delayed_until)  # Needed????
                route_list[1].append(i)  # TODO make choice of route dynamic???
                package_id_list.remove(i)
        elif package.notes.startswith('Wrong address'):
            route_list[2].append(i)  # TODO make choice of route dynamic???
            package_id_list.remove(i)

    for i in package_id_list[:]:  # Distribute the rest of the packages.
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

    for i in package_id_list:  # Assign all other packages to the lists.
        for j in range(len(route_list)):
            if len(route_list[j]) < 16:
                route_list[j].append(i)
                break
    # TODO perhaps implement req following in this first itr. Then optimize w/ annealing.
    # start = ' HUB'
    # start_location = graph_instance.get_vertex(start)
    # num_routes = ceil(num_packages / 16)
    # package_list = [[] for _ in range(num_routes)]
    # vertex_list = [[start_location] for _ in range(num_routes)]
    #
    # for i in range(0, num_routes):  # Create specified number of package_list lists
    #     for j in range(i*15, (i*15)+15):  # Each truck can only hold 16 packages. Add <= 16 packages to each list.
    #         if j <= num_packages-1:  # When total # of packages is exhausted, break from loop.
    #             package_list[i].append(j+1)
    #             # destination_vertex = None  # If using this, need to get vertex by searching from packages address.
    #             vertex_list[i].append(graph_instance.get_vertex(j+1))
    #         else:
    #             break
    #     # print(len(package_list[i]))
    #
    # for sublist in vertex_list:  # Return to hub
    #     sublist.append(start_location)

    return route_list


def swap_two(routes_list, ra_num, rb_num, a, b):
    new_routes = deepcopy(routes_list)
    new_routes[ra_num][a], new_routes[rb_num][b] = new_routes[rb_num][b], new_routes[ra_num][a]
    return new_routes


def two_opt(input_lists):  # TODO whenever swapping indices in vertex_list, must also swap same indices in package_list.
    #                             remember vertex_list > package_list by 2, because hub is at beginning and end!
    routes = deepcopy(input_lists)
    mileage = find_mileages(routes)
    d1 = sum(mileage)

    # new_routes = deepcopy(routes)

    improve = 0
    while improve < 1:

        if random() < 5:
            rn = randint(0, len(routes) - 1)
            #rn = 0

            for i in range(0, len(routes[rn]) - 1):

                for k in range(i+1, len(routes[rn])):

                    # new_routes[rn][i], new_routes[rn][k] = new_routes[rn][k], new_routes[rn][i]

                    new_routes = swap_two(routes, rn, rn, i, k)

                    new_mileage = update_distances(routes, rn, rn, i, k, mileage)
                    # new_mileage = find_mileages(new_routes)
                    print()
                    print('old d')
                    print(d1)
                    print('new d')
                    d2 = sum(new_mileage)
                    print(d2)
                    if d2 < d1:
                        print('         accepted')
                        routes = new_routes
                        mileage = new_mileage
                        print(routes)
                        print(sum(find_mileages(routes)))
                        print()

                        d1 = d2
                        improve = 0

        else:
            ra_num = randint(0, len(routes) - 1)  # Random route a, by index
            rb_num = choice([x for x in range(len(routes) - 1) if x != ra_num])  # Route b, must differ from ra_num

            for i in range(0, len(routes[ra_num]) - 1):

                for k in range(i + 1, len(routes[rb_num])):

                    # new_routes[ra_num][i], new_routes[rb_num][k] = new_routes[rb_num][k], new_routes[ra_num][i]
                    new_routes = swap_two(routes, ra_num, rb_num, i, k)

                    new_mileage = update_distances(routes, ra_num, rb_num, i, k, mileage)
                    d2 = sum(new_mileage)
                    if d2 < d1:
                        routes = new_routes
                        print(routes)
                        mileage = new_mileage
                        d1 = d2
                        improve = 0
        improve += 1
    # print(len(vertex_list))
    # print(len(package_list))
    return routes


def create_new_route(routes_list, distances):
    # TODO this uses SWAPS, try it then test using method w only single element moves
    """
    Swaps a 2 elements within a route, or swaps two elements in separate routes with a 50% chance.
    Requires O(2N) Space  # Worded correctly???????????????

    :param routes_list: The list of routes to be optimized
    :param distances: List of distances for each sub route in routes_list
    :return: new_routes a valid neighbor of routes_list
             new_distances the list of distances of the new_routes list
    """
    new_routes = deepcopy(routes_list)  # Copy of the routes_list
    # new_distances = distances.copy()

    if random() < .5:  # Swap 2 elements within the same list. 50% chance
        rn = randint(0, len(new_routes) - 1)  # TODO do i need the -1 on all these??

        a = randint(0, len(new_routes[rn]) - 1)  # random element from the list by index
        b = choice([i for i in range(len(new_routes[rn]) - 1) if i != a])  # random element must differ from a

        # Swap the two elements
        new_routes[rn][a], new_routes[rn][b] = new_routes[rn][b], new_routes[rn][a]

        # Calculate new distance
        new_distances = update_distances(routes_list, rn, rn, a, b, distances)
    else:  # Swap 2 elements from different lists. 50% chance TODO BROKEN!!!!! FIX THIS FIRST i don't think it's switching like it should!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # TODO also try a greedy algo first before attempting SA. (just do if < 16 packages, next package = closest.)
        ra_num = randint(0, len(new_routes) - 1)  # Random route a, by index
        rb_num = choice([i for i in range(len(new_routes)-1) if i != ra_num])  # Random route b, must differ from ra_num

        a = randint(0, len(new_routes[ra_num]) - 1)  # random element from ra_num route list, by index
        b = randint(0, len(new_routes[rb_num]) - 1)  # random element from rb_num route list, by index

        # Swap the two elements
        new_routes[ra_num][a], new_routes[rb_num][b] = new_routes[rb_num][b], new_routes[ra_num][a]

        # Calculate new distance
        new_distances = update_distances(routes_list, ra_num, rb_num, a, b, distances)

    # TODO maybe change next 2 lines and have SA just move onto it's next itr and return back the original list if False
    # if new_routes is not is_valid(new_routes):  # If the new_route is not valid, go back and make another random move.
    #     new_routes = create_new_route(routes_list, distances)
    return new_routes, new_distances


def simulated_annealing(initial_route):
    routes = initial_route  # List of the routes TODO make copy??
    mileage = find_mileages(routes)  # Distances of each sub route in route
    d1 = sum(mileage)  # Total distance of route

    temp = 70  # Initial Temperature set to 80° ?? y decimal and no just 80?? need to test vars!
    target_temp = 0.5
    cooling_factor = 0.95

    inner_itr = 6000  # variable for num of iterations for exploiting local search area Paper sets this as 6000,overkill
    k = 25  # variable for calculating acceptance probability TODO might not need k! test different variables for best
    # k >= 1
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

            # TODO implement req checker on new_route. if not a valid route then have a var that stores that
            #   and us that for calculation?? checking?? weights in the probability???
            #   Perhaps use the same/similar method in the actual swapping process???

            #   TODO also! for package 9, treat like delivery window after 10:20, cannot be delivered until then.

            # probability formula. Initially, high probability of accepting wrong solutions. As temp decreases,
            #   the probability will decrease and tend toward 0 for worse routes. The algorithm will move
            #   deterministically, only accepting better solutions.
            # source: https://stats.stackexchange.com/questions/453309/what-is-the-relationship-between-metropolis-hastings-and-simulated-annealing
            # TODO in comment here site source as wiki or a paper that has the formula, rather than a forum comment.

            if d2 < d1:  # TODO add AND if d2 is acceptable, if it isn't then only accept if d1 is also not acceptable.
                routes = new_route.copy()
                # print('less')
                # print()
                d1 = d2  # ??+
                # print()
                # print('                                                       better')
            elif d2 > d1:  # if new_route is not better, accept change with probability
                # probability = 1 / (exp(((d2 - d1) * k) / (d1 * temp)))  # TODO try catch w/ if it's math error than = 0?
                try:
                    probability = 1 / (exp((d2 - d1) / temp))
                except OverflowError:
                    probability = 0
                print('temp')
                print(temp)
                print('prob')
                print(probability)

                if random() < probability:
                    # print('ACCEPTEDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD')
                    routes = new_route.copy()
                    d1 = d2  # ??

        temp = temp * cooling_factor
        # print(temp)
    # print('routes= ')
    # print(routes)
    # print('count')
    # print(count)
    # print('bad')
    # print(bad)

    return routes


def is_valid(route_lists):
    valid = True
    for i in range(0, len(route_lists)):
        for k in route_lists[i]:
            package = packages_hash.search(route_lists[i][k])
            if package.deadline < package.status:  # TODO needs work
                valid = False
                break
            if package.notes.startswith('Can only be'):
                if package.notes[-1] != i+1:  # If the package is not on the correct route list (truck num - 1)
                    valid = False
                    break
    return valid


def find_mileages(package_lists):  # TODO might just need the total instead of list of each one??
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
    new_d = distances.copy()  # TODO change so new_distances is calculation of distance_changes with distances.

    package_a = packages_hash.search(routes_list[route_a][element_a])
    a = graph_instance.get_vertex(package_a.get_address())
    package_b = packages_hash.search(routes_list[route_b][element_b])
    b = graph_instance.get_vertex(package_b.get_address())
    hub = graph_instance.get_vertex(' HUB')
    # distance_changes = [[] for _ in range(len(distances))]

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

    # if element_a != element_b-1:  # If they are not neighbors in the route list, swap edge vertices for a+1 and b-1
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
    for truck in loaded_truck:  # TODO change to a single truck for the method. So truck 1 can call deliver(truck1) for
        #                               completing it's second route???????????? unless i'm not doing dynamic num of
        #                               of trucks? so it would loop through the 3 instead of how it is now. and the last
        #                               one just gets the start time from truck 1s end time?
        for package_id in truck.package_list:
            package = packages_hash.search(package_id)
            current_location = graph_instance.get_vertex(truck.location)
            next_location = graph_instance.get_vertex(package.get_address())
            print(package_id)
            distance = graph_instance.get_distance(current_location, next_location)  # in miles
            seconds_taken = int(distance // (truck.speed / 3600))
            # minutes_taken = int(distance // (loaded_truck.speed / 60))
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
        #  Next 7 lines used just for returning to hub.. matches a lot of other lines. TODO Make separate function??
        start = ' HUB'
        hub = graph_instance.get_vertex(start)
        distance = graph_instance.get_distance(graph_instance.get_vertex(truck.location), hub)
        minutes_taken = int(distance // (truck.speed / 60))
        # loaded_truck.time = time_string_forward(loaded_truck.time, minutes_taken)
        truck.miles_traveled += distance
        truck.location = start
        # return_to_hub =
        mileage += truck.miles_traveled
        print(truck.miles_traveled)
        print(truck.time)
        print(packages_delivered)
        print(truck.package_list)
        print()
    print()
    print('mileage')
    print(mileage)

# paths to the csv files
data_path = Path("data/WGUPS Package File.csv")
data_path_destination = Path("data/WGUPS Distance Table.csv")

# initialize the ChainingHashTable instance
packages_hash = controller.hashing_with_chaining.ChainingHashTable()

# initialize the Graph instance. Input set as n^2, where n = the number of destinations in 'WGUPS Distance Table.csv' to
#   reduce collisions and keep lookup time as close to O(1) as possible.
graph_instance = controller.graph.Graph(729)

# second argument = the number of header lines to skip in the csv file before processing the data.
load_package_data(data_path, 8)
load_destination_data(data_path_destination, 8)

# user_search()

trucks = load_trucks(40)  # TODO each truck only holds 16 packages, 2 drivers. so one driver will need to return to
#                                   hub to change trucks (or reload with remaining packages, doesn't need to change
#                                   trucks necessarily, b/c load times are instantaneous.

deliver(trucks)


print()
print('delivered')
print()
for n in range(1, 41):
    print(packages_hash.search(n))

# print('Test probability:')
# print(exp(- (20.0-5) / (40 * .80)))
# TODO okay, I think i'll make the truck amount be static, and in the 'what would you change' section of the paper,
#   i could include implementing a dynamic number of truck choices. This also means that 'Move 2' in the paper
#   might not be needed? maybe?? actually yeah, i don't think i need it b/c truck # doesn't matter, just mileage.
