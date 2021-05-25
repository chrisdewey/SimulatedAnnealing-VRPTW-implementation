all_addresses = []  # To store addresses in order from Distance table, allowing look-up by index.


class Destination:
    def __init__(self, place_num, name, address, distances):
        self.place_num = place_num
        self.name = name
        self.address = address
        self.distances = distances

    def __str__(self):  # used to overwrite print(destination), else it prints the memory reference
        return "%s, %s, %s, %s" % (self.place_num, self.name, self.address, self.distances)
