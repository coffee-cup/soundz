from pydub import AudioSegment
import os.path
import glob
from tinytag import TinyTag
from tqdm import tqdm
from config import get_config


def ensure_directory_exists(name):
    """Checks if the directory name exists."""
    return os.path.exists(name) and not os.path.isfile(name)


def process_mp3_directory(path, fn):
    for filename in tqdm(
            glob.iglob('{}/**/*.mp3'.format(path), recursive=True)):
        fn(filename)


def create_database_directory(name):
    """Create audio database directory if it does not exists."""
    if not os.path.exists(name):
        os.makedirs(name)


def get_song_filename(filename, db_directory, format='wav'):
    """Creates a filepath to a song based on the mp3 metadata."""
    tag = TinyTag.get(filename)
    title = tag.title.replace('/', '').replace('  ', ' ')
    return '{}/{}/{}/{}.{}'.format(db_directory, tag.artist, tag.album, title,
                                   format)


def save_mp3_as_wav(filename, config, format='wav'):
    """Converts filename to wav and saves to file in wav directory."""

    # Create output path for the wav file
    out_path = get_song_filename(filename, config.db_directory, format)

    # If the output filename already exists, just move on
    if os.path.exists(out_path):
        return

    print(out_path)
    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))

    # Read the MP3 file
    song = AudioSegment.from_mp3(filename)

    # Export
    song.export(out_path, format=format)


if __name__ == '__main__':
    config, unparsed = get_config()
    if len(unparsed) <= 0:
        print('Directory to recursivley search for MP3 files is required.')
        exit(1)

    audio_dir = unparsed[0]
    if not ensure_directory_exists(audio_dir):
        print('Directory {} does not exists'.format(audio_dir))
        exit(1)

    create_database_directory(config.db_directory)
    process_mp3_directory(audio_dir, lambda f: save_mp3_as_wav(f, config))
