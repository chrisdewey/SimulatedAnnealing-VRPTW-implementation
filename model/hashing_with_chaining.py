class ChainingHashTable:

    def __init__(self, initial_capacity=10):
        """
        Initializes the hash table.

        Time Complexity: O(1)
        Space Complexity: O(N) where N = the number of buckets the hash table has

        :param initial_capacity: Optional parameter, how many buckets the hash table should have. Default = 10
        """
        self.table = []
        for i in range(initial_capacity):
            self.table.append([])

    def insert(self, item, key):  # inserts the item as a [key, item] pair into the bucket
        """
        Inserts the item into the hash table.

        Time Complexity: Worst Case O(N)  when all elements hash to the same bucket
                         Average Case O(1)
        Space Complexity: O(N)

        :param item:
        :param key:
        """
        bucket = hash(key) % len(self.table)
        buckets_list = self.table[bucket]

        for i in buckets_list:
            if i[0] == key:  # if key is already in the buckets_list, update item
                i[1] = item
                return

        new_item = [key, item]
        buckets_list.append(new_item)

    def search(self, key):  # finds the item in the buckets_list and if found return the item, else return None
        """
        Uses the key to find and return the item in the hash table.

        Time Complexity: Worst Case O(N)  when all elements hash to the same bucket
                         Average Case O(1)
        Space Complexity: O(1)

        :param key:
        :return: The item in the hash table with the given key
        """
        bucket = hash(key) % len(self.table)
        buckets_list = self.table[bucket]

        for i in buckets_list:
            if i[0] == key:
                return i[1]
        return None
