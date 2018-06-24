import numpy as np
from matplotlib import pyplot as plt
import scipy.io.wavfile as wav
from scipy import signal


class Audio(object):
    def __init__(self, filename, samples, samplerate, frame_size, freqs, times,
                 spec):
        self.filename = filename
        self.samples = samples
        self.samplerate = samplerate
        self.frame_size = frame_size
        self.freqs = freqs
        self.times = times
        self.spec = spec
        self.length = samples.shape[0] / samplerate


def process_wav_file(filename):
    samplerate, samples = wav.read(filename)

    # Convert stereo to mono
    samples = samples.sum(axis=1) / 2

    frame_size = 1024
    window = 'hamming'
    overlap = np.floor(0.5 * frame_size)
    nfft = frame_size
    scaling = 'spectrum'

    print('Sample rate: {}'.format(samplerate))
    print('Length: {:.2f} sec'.format(samples.shape[0] / samplerate))
    print('Window size: {:.2f} ms'.format(frame_size / samplerate * 1000))

    freqs, times, spec = signal.spectrogram(
        samples,
        samplerate,
        window=window,
        nperseg=frame_size,
        noverlap=overlap,
        nfft=nfft,
        scaling=scaling)

    s = Audio(filename, samples, samplerate, frame_size, freqs, times, spec)
    return s


def graph_spectrogram(audio, colormap="jet"):
    """Plot spectrogram."""

    plt.figure(figsize=(10, 5))
    plt.pcolormesh(
        audio.times, audio.freqs, 10 * np.log10(audio.spec), cmap=colormap)
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.xlim(0, np.floor(audio.length))
    plt.show()
