class Song(object):
    def __init__(self, filename, meta, samples, sr):
        super(Song, self).__init__()

        self.filename = filename
        self.meta = meta
        self.samples = samples
        self.samplerate = sr
