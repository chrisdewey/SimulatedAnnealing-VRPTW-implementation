from math import exp
from random import random, randint, choice
from copy import deepcopy
from datetime import datetime, date


def simulated_annealing(p_hash, graph_instance, initial_route):
    """


    :param p_hash:
    :param graph_instance:
    :param initial_route:
    :return:
    """
    routes = initial_route  # List of the routes
    mileage = find_mileages(p_hash, graph_instance, routes)  # Distances of each sub route in route
    d1 = sum(mileage)  # Total distance of route

    temp = 100  # Initial Temperature set to 80° ?? y decimal and no just 80?? need to test vars!
    target_temp = 0.5
    cooling_factor = 0.995

    inner_itr = 60  # variable for num of iterations for exploiting local search area Paper sets this as 6000,overkill

    while temp > target_temp:
        for i in range(inner_itr):
            neighbor = create_new_route(p_hash, graph_instance, routes, mileage)
            new_route = neighbor[0]
            new_mileage = neighbor[1]  # Distance of new_route

            d2 = sum(new_mileage)  # Total distance of new_mileage

            # probability formula. Initially, high probability of accepting wrong solutions. As temp decreases,
            #   the probability will decrease and tend toward 0 for worse routes. The algorithm will move
            #   deterministically, only accepting better solutions.
            # source: https://stats.stackexchange.com/questions/453309/what-is-the-relationship-between-metropolis-hastings-and-simulated-annealing
            # TODO in comment here site source as wiki or a paper that has the formula, rather than a forum comment.

            # if d2 = d1, then do nothing... TODO or would it be better to make last ELSE be accept, meaning accept if =
            if d2 < d1:
                routes = new_route.copy()
                d1 = d2
            elif d2 > d1:  # if new_route is not better, accept change with probability
                try:
                    probability = 1 / (exp((d2 - d1) / temp))
                except OverflowError:
                    probability = 0

                if random() < probability:
                    routes = new_route.copy()
                    d1 = d2

        temp = temp * cooling_factor

    return routes


def find_mileages(p_hash, graph_instance, package_lists):
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
        package = p_hash.search(package_lists[i][0])
        hub = graph_instance.get_vertex(' HUB')
        package_address = graph_instance.get_vertex(package.get_address())
        mileage[i] += graph_instance.get_distance(hub, package_address)

        for j in range(len(package_lists[i])-1):
            next_package = p_hash.search(package_lists[i][j + 1])
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


def create_new_route(p_hash, graph_instance, routes_list, distances):
    """
    Randomly selects between 2 types of moves:
        1. Swaps 2 elements within a single route
        2. Swaps 2 elements from different routes
    If the swaps are invalid, return the original routes_list

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

    :param routes_list:
    :param route_a:
    :param route_b:
    :param element_a:
    :param element_b:
    :param distances:
    :param p_hash:
    :param graph_instance:
    :return: The updated list of distances.
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
