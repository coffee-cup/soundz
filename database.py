from sqlalchemy import Column, ForeignKey, Integer, String, Float, Binary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm
import psycopg2

Base = declarative_base()


class Song(Base):
    __tablename__ = 'song'

    id = Column(Integer, primary_key=True)
    artist = Column(String, nullable=False)
    album = Column(String, nullable=False)
    title = Column(String, nullable=False)
    track = Column(String)
    year = Column(Integer)
    samplerate = Column(Integer)
    duration = Column(Float)


class Fingerprint(Base):
    __tablename__ = 'fingerprint'

    id = Column(Integer, primary_key=True)
    hash = Column(Binary, nullable=False)
    time = Column(Integer, nullable=False)
    song_id = Column(Integer, ForeignKey('song.id'), nullable=False)
    song = relationship(Song)


url = 'postgresql://soundz:soundz@localhost:5432/soundz'
engine = create_engine(url)

Base.metadata.create_all(engine)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def save_song(song):
    """Saves a song into the database."""
    new_song = Song(
        artist=song.meta.artist,
        album=song.meta.album,
        title=song.meta.title,
        track=song.meta.track,
        year=song.meta.year,
        samplerate=song.meta.samplerate,
        duration=song.meta.duration)

    session.add(new_song)
    session.commit()

    return new_song


def lookup_song(song_id):
    """Lookup and return a song by id."""
    song = session.query(Song).filter(Song.id == song_id).first()
    return song


def save_fingerprints(song, fingerprints):
    """
    Save list of fingerprints to the database.
    The fingerprints are linked to the song.
    """
    print('Saving fingerprints')

    inserts = []
    for p in tqdm(fingerprints):
        new_fingerprint = Fingerprint(
            hash=p.hash, time=p.time, song=song, song_id=song.id)
        inserts.append(new_fingerprint)

    session.bulk_save_objects(inserts)
    session.commit()


def lookup_fingerprints(fingerprints):
    """Get all fingerprints that are in the list of fingerprints."""
    hashes = list(map(lambda f: f.hash, fingerprints))
    matches = session.query(Fingerprint).filter(
        Fingerprint.hash.in_(hashes)).all()
    return matches


def does_song_exist(song):
    """Returns if the song is already in the database."""
    count = session.query(Song).\
        filter(Song.artist == song.meta.artist).\
        filter(Song.album == song.meta.album).\
        filter(Song.track == song.meta.track).\
        count()

    return count != 0
