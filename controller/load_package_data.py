import csv
from model.package import Package
import controller.quadratic_probing_hash


def load_items(input_data, header_lines):
    with open(input_data) as items:
        data = csv.reader(items, delimiter=',')

        for i in range(0, header_lines):
            next(data, None)  # skip specified number of header lines

        for item in data:  # parse data into separate items
            new_id = int(item[0])
            new_address = item[1]
            new_city = item[2]
            new_state = item[3]
            new_zip = item[4]
            new_deadline = item[5]
            new_mass = item[6]
            new_notes = item[7]

            # create item object
            new_item = Package(new_id, new_address, new_city, new_state, new_zip, new_deadline, new_mass, new_notes)

            # HashInstance.insert(new_item, new_id)
            # print(HashInstance.search(new_id))

# Might want to use this instead of having the method inside of main.py ??? -> would need to pass HashInstance
#   either that or initialize the instance here, but if need to access it later could be problematic ???
