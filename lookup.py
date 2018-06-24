import pyaudio
import numpy as np
from audio import preprocess, generate_fingerprints
from database import lookup_fingerprints, lookup_song

CHUNK = 4096
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100


def align_matches(matches):
    """Finds most probably match based on offset time."""
    diff_counter = {}

    largest = 0
    largest_count = 0
    matched_song = -1

    for tup in matches:
        song_id, diff = tup
        if diff not in diff_counter:
            diff_counter[diff] = {}
        if song_id not in diff_counter[diff]:
            diff_counter[diff][song_id] = 0

        diff_counter[diff][song_id] += 1

        if diff_counter[diff][song_id] > largest_count:
            largest = diff
            largest_count = diff_counter[diff][song_id]
            matched_song = song_id

    print('matched {}'.format(matched_song))
    song = lookup_song(matched_song)
    matched_info = {
        'artist': song.artist,
        'album': song.album,
        'title': song.title,
        'offset': largest
    }

    return matched_info


def find_matches(samples, sr=RATE):
    """Finds fingerprint matches for the samples."""
    print('Finding matching fingerprints...')

    samples = preprocess(samples, sr)
    fingerprints = generate_fingerprints(
        'Microphone', samples, sr=sr, plot=True)

    print('Looking up matches in database...')
    matches = lookup_fingerprints(fingerprints)
    print('{} Matches'.format(len(matches)))

    if len(matches) == 0:
        return None

    mapper = {}
    for f in fingerprints:
        mapper[f.hash] = f.time

    diffed_matches = []
    for f in matches:
        diffed_matches.append((f.song_id, f.time - mapper[f.hash]))

    return diffed_matches


def find_microphone_matches():
    data = record_audio(seconds=10)
    matches = find_matches(data)

    if matches is None:
        print('No Matches :(')
    else:
        song = align_matches(matches)

        print('----- Match')
        print(song['title'])
        print(song['artist'])
        print(song['album'])


def record_audio(seconds=5):
    """Records seconds of audio and returns the data."""
    p = pyaudio.PyAudio()

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK)
    print('Recoring for {} seconds'.format(seconds))

    data = [[] for i in range(CHANNELS)]
    sec = 0
    chunks_sec = RATE / CHUNK
    for i in range(0, int(chunks_sec * seconds)):
        d = stream.read(CHUNK)
        nums = np.fromstring(d, np.int16)
        for c in range(CHANNELS):
            data[c].extend(nums[c::CHANNELS])

        new_sec = int(i / chunks_sec)
        if new_sec > sec:
            sec = new_sec
            print(seconds - sec)
    print('Done!')

    stream.stop_stream()
    stream.close()

    return np.array(data).transpose()


if __name__ == '__main__':
    find_microphone_matches()
