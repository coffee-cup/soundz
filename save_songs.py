from pydub import AudioSegment
import os.path
import glob
import scipy.io.wavfile as wav
from tinytag import TinyTag
from config import get_config
from audio import preprocess, generate_fingerprints
from song import Song
from database import does_song_exist, save_song, save_fingerprints


def process_mp3_directory(path, fn):
    for filename in glob.iglob('{}/**/*.mp3'.format(path), recursive=True):
        fn(filename)


def read_mp3(filename):
    """Read MP3 file into a Song object."""
    if not os.path.isfile(filename):
        print('{} does not exists'.format(filename))
        exit(1)

    # Read metadata from song
    meta = TinyTag.get(filename)

    # Read mp3 and save as tempoary wavfile
    song = AudioSegment.from_mp3(filename)
    tmp_path = './tmp_{}'.format(os.path.basename(filename))
    song.export(tmp_path, format='wav')

    # Read and delete tempory wavefile
    samplerate, samples = wav.read(tmp_path)
    os.remove(tmp_path)

    samples = preprocess(samples, samplerate)

    s = Song(filename, meta, samples, samplerate)
    return s


def process_mp3(filename):
    """
    Creates a fingerprint for an mp3 file and saves it into the database.
    """
    song = read_mp3(filename)

    print('---------------------')
    print('Processing {}...'.format(filename))
    print('Title  : {}'.format(song.meta.title))
    print('Artist : {}'.format(song.meta.artist))
    print('Album  : {}'.format(song.meta.album))
    print('')

    if not does_song_exist(song):
        prints = generate_fingerprints(
            song.meta.title, song.samples, song.samplerate, plot=False)
        db_song = save_song(song)
        save_fingerprints(db_song, prints)

    else:
        print('Song already exists')


if __name__ == '__main__':
    config, unparsed = get_config()
    if len(unparsed) <= 0:
        print('Directory to recursivley search for MP3 files is required.')
        exit(1)

    path = unparsed[0]
    if not os.path.exists(path):
        print('{} file or directory does not exists'.format(path))
        exit(1)

    if os.path.isfile(path):
        # Process single file
        process_mp3(path)
    else:
        # Process directory of MP3s
        process_mp3_directory(path, lambda f: process_mp3(f))
