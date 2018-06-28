class Fingerprint(object):
    def __init__(self, hash, time):
        super(Fingerprint, self).__init__()

        self.hash = hash.encode('utf-8')
        self.time = int(time)

    def __str__(self):
        return '{}:{}'.format(self.hash, self.time)

    def __eq__(self, other):
        return isinstance(
            other, self.__class__
        ) and other.hash == self.hash and other.time == self.time

    def __hash__(self):
        return hash(self.hash) ^ hash(self.time)
