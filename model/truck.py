class Truck:
    def __init__(self, truck_num, packages, route, speed=18):
        self.truck_num = truck_num
        self.packages = packages
        self.location = 'at hub'  # trucks start at hub
        self.time = None
        self.time_left_hub = None
        self.route = route
        self.speed = speed  # in mph
        self.miles_traveled = 0.0

    def packages(self):
        for i in range(0, len(self.packages)):
            print(self.packages(i))

    def __str__(self):
        return "%s, %s, %s" % (self.truck_num, self.packages, self.location)

# things the Truck class needs = location, time, time left hub, package/weight limit (depending on req.s)
