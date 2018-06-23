from config import get_config
from audio import process_wav_file, graph_spectrogram


if __name__ == '__main__':
    config, unparsed = get_config()

    if len(unparsed) <= 0:
        print('Wav file required as argument.')
        exit(1)

    audio_path = unparsed[0]
    audio = process_wav_file(audio_path)
    graph_spectrogram(audio)
