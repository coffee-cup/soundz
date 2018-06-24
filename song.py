class Song(object):
    def __init__(self, filename, meta, samples, sr):
        super(Song, self).__init__()

        self.filename = filename
        self.meta = meta
        self.samples = samples
        self.samplerate = sr

        if meta is not None:
            self.artist = meta.artist
            self.album = meta.album
            self.title = meta.title
            self.track = meta.track
            self.duration = meta.duration
            self.samplerate = meta.samplerate
            self.year = meta.year
