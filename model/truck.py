class Truck:
    def __init__(self, truck_num, package_list, time_to_leave_hub, speed=18):
        """
        Initializes a truck object.
        """
        self.truck_num = truck_num
        self.package_list = package_list
        self.location = ' HUB'  # trucks start at hub
        self.time = time_to_leave_hub
        self.time_left_hub = time_to_leave_hub
        self.speed = speed  # in mph
        self.miles_traveled = 0.0

    def __str__(self):
        return "%s, %s, %s" % (self.truck_num, self.package_list, self.location)
