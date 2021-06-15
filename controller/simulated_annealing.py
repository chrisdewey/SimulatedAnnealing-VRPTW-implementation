from math import exp
from random import random, randint, choice
from copy import deepcopy
from datetime import datetime, date


def simulated_annealing(p_hash, graph_instance, initial_route):
    """
    Implementation of the Simulated Annealing algorithm. The algorithm uses the analogy to real world metal annealing
    of 'cooling down' it's 'temperature' (temp) as it iterates.
    Firstly, we generate a neighbor to the initial_route by calling create_new_route() which randomly swaps 2 vertices,
    so long as they do not invalidate the route. Then, compare the mileage from the new route to that of the current
    route. We accept the new route as the current if it requires less mileage. If the new route is worse than the
    current, we probabilistically accept the new route as the current solution. This probability tends toward 0 as the
    'temp' approaches the 'target_temp' and is given by: probability = 1 / (exp((d2 - d1) / temp))
    Therefore, the lower 'temp' is the less likely the algorithm is to accept a worse solution.
    - https://en.wikipedia.org/wiki/Simulated_annealing

    Because Simulated Annealing is a stochastic method, a different result is obtained each run. However, optimizing the
    variables 'temp', 'target_temp', and 'cooling_factor' allows us to tune the algorithm for accuracy, often resulting
    in a trade-off between accuracy and runtime. All of these changes individually increase the runtime, as well as the
    potential accuracy (due to increasing the number of iterations of create_new_route() and choosing solutions):
        Increasing starting value of 'temp'
        Decreasing 'target_temp' closer to 0, but not = to 0
        increasing 'cooling_factor' closer to 1, but not = to 1

    can recursively call SA for better results? maybe a better way of choosing a neighbor rather than complete
    randomization would be more efficient.. but how?
    however the vars temp etc were arbitrarily chosen and through trial and error were tweaked until a satisfactory
    result - this is not optimal

    Time Complexity: Worst Case O(N*M) where N from create_new_route()'s worst case, and M = the number of times the
                                          function iterates. M is a constant but very large value from temp given by:
                                          M = ⌈ log(target_temp/temp)/log(cooling_factor)⌉
                     Average Case O(N+M) where N from find_mileages() which is called once, and
                                          M = ⌈ log(target_temp/temp)/log(cooling_factor)⌉
    Space Complexity: O(1)
    With the current variables set at target_temp=0.00001, temp=240, and cooling_factor=0.9999; M=339863 iterations.

    :param p_hash: hash storing package data
    :param graph_instance: graph storing destination and distance data
    :param initial_route: the route to be optimized
    :return: an optimized route list (list of sub routes)
    """
    routes = initial_route  # List of the routes
    mileage = find_mileages(p_hash, graph_instance, routes)  # Distances of each sub route in route
    d1 = sum(mileage)  # Total distance of route

    temp = 240  # Initial Temperature
    target_temp = 0.00001
    cooling_factor = 0.99995

    while temp > target_temp:
        neighbor = create_new_route(p_hash, graph_instance, routes, mileage)
        new_route = neighbor[0]
        new_mileage = neighbor[1]  # Distance of new_route

        d2 = sum(new_mileage)  # Total distance of new_mileage

        # Note that if d2 = d1, we do not accept the new_route
        if d2 < d1:
            routes = new_route.copy()
            d1 = d2
        elif d2 > d1:  # If new_route is not better then the current route, accept the change with probability
            try:
                probability = 1 / (exp((d2 - d1) / temp))
            except OverflowError:
                probability = 0

            if random() < probability:
                routes = new_route.copy()
                d1 = d2

        temp = temp * cooling_factor

    return routes


def find_mileages(p_hash, graph_instance, route_lists):
    """
    Calculates the total mileage a route will take from start to finish. For each route list, the function
    first finds the distance from the HUB to the first packages' key. Then loops through the rest of the packages
    and adds the distance. Finally finds the distance from the final key back to the HUB.

    Time Complexity: O(N)  where N = the total number of packages (split between each route)
    Space Complexity: O(1)

    :param p_hash: hash holding all of the package date
    :param graph_instance: graph holding all the distance and destination data
    :param route_lists: the routes_list
    :return: a list of mileages for each route in routes_list
    """
    mileage = [0.0 for _ in range(0, 3)]
    for i in range(0, 3):  # Loop through route_lists, which = 3 because there are 3 routes.
        # Find mileage from HUB to first Address
        package = p_hash.search(route_lists[i][0])
        hub = graph_instance.get_vertex(' HUB')
        package_address = graph_instance.get_vertex(package.get_address())
        mileage[i] += graph_instance.get_distance(hub, package_address)

        for j in range(len(route_lists[i]) - 1):  # Loop through each routes packages
            next_package = p_hash.search(route_lists[i][j + 1])
            next_address = graph_instance.get_vertex(next_package.get_address())

            mileage[i] += graph_instance.get_distance(package_address, next_address)

            package = next_package
            package_address = next_address

        # Find mileage from the last key back to the HUB
        mileage[i] += graph_instance.get_distance(package_address, hub)
        # print('mileage ' + str(i))
        # print(mileage[i])
        # print()
    return mileage


def create_new_route(p_hash, graph_instance, routes_list, distances):
    """
    Randomly selects between 2 types of moves:
        1. Swaps 2 elements within a single route
        2. Swaps 2 elements from different routes
    If the swaps are invalid, return the original routes_list

    Time Complexity: Worst Case O(N) if valid_move() probes a hash table with all elements in the same hash bucket when
                                        searching for the package to validate its move
                     Average Case O(1)
    Space Complexity: O(1)

    :param p_hash:
    :param graph_instance:
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

        if valid_move(p_hash, new_routes, rn, rn, a, b):
            # Swap the two elements
            new_routes[rn][a], new_routes[rn][b] = new_routes[rn][b], new_routes[rn][a]

            # Calculate new distance
            new_distances = update_distances(p_hash, graph_instance, routes_list, rn, rn, a, b, distances)

    else:  # Swap 2 elements from different lists. 50% chance
        ra_num = randint(0, len(new_routes) - 1)  # Random route a, by index
        rb_num = choice([i for i in range(len(new_routes)-1) if i != ra_num])  # Random route b, must differ from ra_num

        a = randint(0, len(new_routes[ra_num]) - 1)  # random element from ra_num route list, by index
        b = randint(0, len(new_routes[rb_num]) - 1)  # random element from rb_num route list, by index

        if valid_move(p_hash, new_routes, ra_num, rb_num, a, b):
            # Swap the two elements
            new_routes[ra_num][a], new_routes[rb_num][b] = new_routes[rb_num][b], new_routes[ra_num][a]

            # Calculate new distance
            new_distances = update_distances(p_hash, graph_instance, routes_list, ra_num, rb_num, a, b, distances)

    return new_routes, new_distances


def update_distances(p_hash, graph_instance, routes_list, route_a, route_b, element_a, element_b, distances):
    """
    Determines the change in the routes distance, taking into account whether either element swapped was
    the first or last package to be delivered in their route.

    Time Complexity: O(1)
    Space Complexity: O(1)

    :param p_hash: hash holding all of the package data
    :param graph_instance: graph holding all of the destination and distances data
    :param routes_list: list of routes
    :param route_a: index of route a in routes_list
    :param route_b: index of route b in routes_list
    :param element_a: index of element a within it's route
    :param element_b: index of element b within it's route
    :param distances: list of distances each route requires
    :return: The updated list of distances for each route in routes_list
    """
    new_d = distances.copy()

    package_a = p_hash.search(routes_list[route_a][element_a])
    a = graph_instance.get_vertex(package_a.get_address())
    package_b = p_hash.search(routes_list[route_b][element_b])
    b = graph_instance.get_vertex(package_b.get_address())
    hub = graph_instance.get_vertex(' HUB')

    if element_a == 0:
        prev_a = hub
    else:
        prev_a_package = p_hash.search(routes_list[route_a][element_a - 1])
        prev_a = graph_instance.get_vertex(prev_a_package.get_address())

    if element_b == 0:
        prev_b = hub
    else:
        prev_b_package = p_hash.search(routes_list[route_b][element_b - 1])
        prev_b = graph_instance.get_vertex(prev_b_package.get_address())

    if element_a == len(routes_list[route_a])-1:
        next_a = hub
    else:
        next_a_package = p_hash.search(routes_list[route_a][element_a + 1])
        next_a = graph_instance.get_vertex(next_a_package.get_address())

    if element_b == len(routes_list[route_b])-1:
        next_b = hub
    else:
        next_b_package = p_hash.search(routes_list[route_b][element_b + 1])
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


def valid_move(p_hash, routes_list, ra_num, rb_num, a, b):
    """
    Validates the proposed route change of swapping elements a and b by checking whether the change would move either
    element to a position that would violate their respective requirements.

    Packages with early morning deadlines (less than 10:30am) are checked to ensure they stay on Truck 1. This would be
    problematic if there are many packages with an early morning deadline.

    Packages with any other deadline besides EOD (end of day) are checked to ensure they are not on Truck 3 (because it
    leaves after Truck 1 returns) and that they are near the beginning of the route. Either < 12 stops if on Truck 1,
    or < 6 stops if on Truck 2(because Truck 2 leaves after 9:05am to accommodate delayed packages). These numbers were
    found by running the optimization program and getting average times when the specified truck would exceed the needed
    time to make the deadline, making the deadline choice dynamic and not scalable.

    Time Complexity: Worst Case O(N) when p_hash.search searches the hash table if all elements are in the same bucket
                     Average Case O(1)
    Space Complexity: O(1)

    :param p_hash: The hash instance housing the package data
    :param routes_list: the current list of routes
    :param ra_num: index number of route a
    :param rb_num: index number of route b
    :param a: The first element to be swapped
    :param b: The second element to be swapped
    :return: False if the proposed swap would create an invalid route, else True
    """
    is_valid = True

    package_a = p_hash.search(routes_list[ra_num][a])
    package_b = p_hash.search(routes_list[rb_num][b])

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

    if package_a.notes.startswith('Delayed'):  # Delayed packages cannot be on Truck 1 (route 0 in routes_list)
        if rb_num == 0:
            is_valid = False
    if package_b.notes.startswith('Delayed'):  # Delayed packages cannot be on Truck 1 (route 0 in routes_list)
        if ra_num == 0:
            is_valid = False

    if package_a.notes.startswith('Wrong'):  # 'Wrong address' packages must be on Truck 3, it leaves the latest
        if rb_num != 2:
            is_valid = False
    if package_b.notes.startswith('Wrong'):  # 'Wrong address' packages must be on Truck 3, it leaves the latest
        if ra_num != 2:
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
