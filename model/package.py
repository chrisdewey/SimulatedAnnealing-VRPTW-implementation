class Package:
    def __init__(self, id_, address, city, state, zip_, deadline, mass, notes, status='at the hub'):
        """
        Initializes a package object.
        """
        self.id_ = id_
        self.address = address
        self.city = city
        self.state = state
        self.zip_ = zip_
        self.deadline = deadline  # EOD = 5:00pm
        self.mass = mass  # Weight given in KG
        self.notes = notes
        self.status = status  # All packages start 'at hub'
        self.timestamp = ''
        self.assigned_truck = None

    def __str__(self):  # used to overwrite print(package), else it prints the reference
        return "%s, %s, %s, %s, %s, deadline: %s, %s, %s, %s, delivered at: %s" %\
               (self.id_, self.address, self.city, self.state,
                self.zip_, self.deadline, self.mass, self.notes, self.status, self.timestamp)

    def get_address(self):  # Returns the key formatted with the zip code
        """
        Returns the address formatted the the zip code.

        Time Complexity: O(1)
        Space Complexity: O(1)

        :return: the address
        """
        return ' ' + self.address + '\n' + '(' + self.zip_ + ')'
