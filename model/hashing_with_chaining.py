class ChainingHashTable:

    def __init__(self, initial_capacity=10):

        self.table = []
        for i in range(initial_capacity):
            self.table.append([])

    def insert(self, item, key):  # inserts the item as a [key, item] pair into the bucket
        bucket = hash(key) % len(self.table)
        buckets_list = self.table[bucket]

        for i in buckets_list:
            if i[0] == key:  # if key is already in the buckets_list, update item
                i[1] = item
                return True

        new_item = [key, item]
        buckets_list.append(new_item)

    def remove(self, key):  # removes the item from the bucket
        bucket = hash(key) % len(self.table)
        buckets_list = self.table[bucket]

        if key in buckets_list:
            buckets_list.remove(key)

    def search(self, key):  # finds the item in the buckets_list and if found return the item, else return None
        bucket = hash(key) % len(self.table)
        buckets_list = self.table[bucket]

        for i in buckets_list:
            if i[0] == key:
                return i[1]
        return None
