class EmptyBucket:
    pass


class HashTable:

    def __init__(self, initial_capacity=10):

        self.EMPTY_SINCE_START = EmptyBucket()
        self.EMPTY_AFTER_REMOVAL = EmptyBucket()

        self.table = [self.EMPTY_SINCE_START] * initial_capacity

    def insert(self, item, key):
        i = 0
        bucket = hash(key) % len(self.table)
        buckets_probed = 0
        while buckets_probed < len(self.table):

            if type(self.table[bucket]) is EmptyBucket:
                self.table[bucket] = item
                print('inserted')
                return True

            i += i
            bucket = (bucket + i + i * i) % len(self.table)
            buckets_probed += 1
        print('f')
        return False

    def remove(self, key):
        i = 0
        bucket = hash(key) % len(self.table)
        buckets_probed = 0
        while self.table[bucket] is not self.EMPTY_SINCE_START and buckets_probed < len(self.table):
            if self.table[bucket] == key:
                self.table[bucket] = self.EMPTY_AFTER_REMOVAL

            i += i
            bucket = (bucket + i + i * i) % len(self.table)
            buckets_probed += 1

    def search(self, key):
        i = 0
        bucket = hash(key) % len(self.table)
        buckets_probed = 0
        while self.table[bucket] is not self.EMPTY_SINCE_START and buckets_probed < len(self.table):
            if self.table[bucket] == key:
                return self.table[bucket]

            i += i
            bucket = (bucket + i + i * i) % len(self.table)
            buckets_probed += 1

        return None
