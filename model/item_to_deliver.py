class Package:
    def __init__(self, id_, address, city, state, zip_, deadline, mass, notes, status='at hub'):
        self.id_ = id_
        self.address = address
        self.city = city
        self.state = state
        self.zip_ = zip_
        self.deadline = deadline  # EOD = End of Day
        self.mass = mass  # Weight given in KG
        self.notes = notes
        self.status = status  # All packages start 'at hub'

    def __str__(self):  # used to overwrite print(package), else it prints the reference
        return "%s, %s, %s, %s, %s, %s, %s, %s, %s" %\
               (self.id_, self.address, self.city, self.state,
                self.zip_, self.deadline, self.mass, self.notes, self.status)
