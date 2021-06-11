from math import ceil
from datetime import datetime, date


def unoptimized_route(packages_hash, num_packages):
    """
    Creates an initial unoptimized route where packages with requirements are considered.

    :param packages_hash: hash instance that houses the package data
    :param num_packages: the number of packages
    :return: an unoptimized list of route lists
    """
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
