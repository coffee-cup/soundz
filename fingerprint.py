class Fingerprint(object):
    def __init__(self, hash, time):
        super(Fingerprint, self).__init__()

        self.hash = hash
        self.time = int(time)

    def __str__(self):
        return '{}:{}'.format(self.hash, self.time)
