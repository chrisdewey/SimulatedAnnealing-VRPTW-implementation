class Truck:
    def __init__(self, truck_num, package_list, time_to_leave_hub, route, speed=18):
        self.truck_num = truck_num
        self.package_list = package_list
        self.location = ' HUB'  # trucks start at hub
        self.time = time_to_leave_hub
        self.time_left_hub = time_to_leave_hub  # not sure i need both variables??
        self.route = route
        self.speed = speed  # in mph
        self.miles_traveled = 0.0

    def packages(self):
        for i in range(0, len(self.package_list)):
            print(self.package_list(i))

    def remove_package(self, package):
        self.package_list.remove(package)

    def __str__(self):
        return "%s, %s, %s" % (self.truck_num, self.package_list, self.location)
