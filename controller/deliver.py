from datetime import datetime, timedelta


def deliver(packages_hash, graph_instance, loaded_truck):
    """
    Loops through each Loaded Truck and delivers the packages they contain in the optimized order given to them by
    visiting their addresses and recording the mileage and time it takes to get there. The packages are timestamped
    when they are delivered. Each Truck returns to the HUB after their delivery route is finished.
    Because there are only 2 drivers, Truck 3 only leaves after Truck 1 returns.

    Time Complexity: Worst Case O(n^2) if packages_hash.search, graph_instance.get_vertex or graph_instance.get_distance
                                         inserts into a hash table where every element is in the same bucket
                     Average Case O(N) where N = the total number of elements in the trucks package lists
    Space Complexity: O(1)

    :param packages_hash:
    :param graph_instance:
    :param loaded_truck: The loaded trucks to deliver packages
    """
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
            # Package w wrong key is updated after 10:30 am. Because it is on Truck 3, it will always be after 10:30
            if package.notes.startswith('Wrong key'):
                package.address = '410 S State St'
                package.city = 'Salt Lake City'
                package.state = 'UT'
                package.zip_ = '84111'
            current_location = graph_instance.get_vertex(truck.location)
            next_location = graph_instance.get_vertex(package.get_address())
            distance = graph_instance.get_distance(current_location, next_location)  # in miles
            seconds_taken = int(distance // (truck.speed / 3600))
            truck.time += timedelta(seconds=seconds_taken)
            package.status = 'Delivered'
            package.timestamp = truck.time

            truck.miles_traveled += distance

            # after delivering package, current truck location is the just delivered packages key.
            truck.location = package.get_address()

            packages_delivered += 1
        # Next 5 lines used just for returning to hub.. matches a lot of other lines. TODO Make separate function??
        start = ' HUB'
        hub = graph_instance.get_vertex(start)
        distance = graph_instance.get_distance(graph_instance.get_vertex(truck.location), hub)
        truck.miles_traveled += distance
        truck.location = start

        mileage += truck.miles_traveled
        print('Truck: ' + str(truck.truck_num))
        print('Miles Traveled: ', end='')
        print(truck.miles_traveled)
        print('Time Returned to HUB: ', end='')
        print(truck.time)
        print('Route: ', end='')
        print(truck.package_list)
        print()
    print('Total Mileage: ', end='')
    print(mileage)
