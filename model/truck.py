class Truck:
    def __init__(self, truck_num, packages, time_to_leave_hub, route, speed=18):
        self.truck_num = truck_num
        self.packages = packages
        self.location = ' HUB'  # trucks start at hub
        self.time = time_to_leave_hub
        self.time_left_hub = time_to_leave_hub  # not sure i need both variables??
        self.route = route
        self.speed = speed  # in mph
        self.miles_traveled = 0.0

    def packages(self):
        for i in range(0, len(self.packages)):
            print(self.packages(i))

    def travel(self, package):
        pass

    def remove_package(self, package):
        self.packages.remove(package)

    def __str__(self):
        return "%s, %s, %s" % (self.truck_num, self.packages, self.location)

# things the Truck class needs = location, time, time left hub, package/weight limit (depending on req.s)
