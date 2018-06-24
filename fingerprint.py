class Fingerprint(object):
    def __init__(self, hash, time):
        super(Fingerprint, self).__init__()

        self.hash = hash.encode('utf-8')
        self.time = int(time)

    def __str__(self):
        return '{}:{}'.format(self.hash, self.time)
