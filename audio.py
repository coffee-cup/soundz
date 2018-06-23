import numpy as np
from matplotlib import pyplot as plt
import scipy.io.wavfile as wav
from numpy.lib import stride_tricks


class Audio(object):
    def __init__(self, filename, samples, time_freq, binsize, samplerate):
        self.filename = filename
        self.samples = samples
        self.time_freq = time_freq
        self.binsize = binsize
        self.samplerate = samplerate


def stft(sig, frame_size, overlap_fac=0.5, window=np.hanning):
    """Short time fourier transform of audio signal."""
    win = window(frame_size)
    hop_size = int(frame_size - np.floor(overlap_fac * frame_size))

    # zeros at beginning (thus center of 1st window should be for sample nr. 0)
    samples = np.append(np.zeros(int(np.floor(frame_size / 2.0))), sig)

    # cols for windowing
    cols = int(np.ceil((len(samples) - frame_size) / float(hop_size)) + 1)

    # zeros at end (thus samples can be fully covered by frames)
    samples = np.append(samples, np.zeros(frame_size))

    frames = stride_tricks.as_strided(
        samples,
        shape=(cols, frame_size),
        strides=(samples.strides[0] * hop_size, samples.strides[0])).copy()
    frames *= win

    return np.fft.rfft(frames)


def process_wav_file(filename, samplerate=44100):
    samplerate, samples = wav.read(filename)

    # Convert stereo to mono
    samples = samples.sum(axis=1) / 2

    binsize = 2**10  # 1024
    time_freq = stft(samples, binsize)

    s = Audio(filename, samples, time_freq, binsize, samplerate)
    return s


def logscale_spec(spec, sr=44100, factor=20.):
    """Scape frequency axis logarithmically."""
    timebins, freqbins = np.shape(spec)

    scale = np.linspace(0, 1, freqbins)**factor
    scale *= (freqbins - 1) / max(scale)
    scale = np.unique(np.round(scale)).astype(int)

    # create spectrogram with new freq bins
    newspec = np.complex128(np.zeros([timebins, len(scale)]))
    for i in range(0, len(scale)):
        if i == len(scale) - 1:
            newspec[:, i] = np.sum(spec[:, scale[i]:], axis=1)
        else:
            newspec[:, i] = np.sum(spec[:, scale[i]:scale[i + 1]], axis=1)

    # list center freq of bins
    allfreqs = np.abs(np.fft.fftfreq(freqbins * 2, 1. / sr)[:freqbins + 1])
    freqs = []
    for i in range(0, len(scale)):
        if i == len(scale) - 1:
            freqs += [np.mean(allfreqs[scale[i]:])]
        else:
            freqs += [np.mean(allfreqs[scale[i]:scale[i + 1]])]

    return newspec, freqs


def graph_spectrogram(audio, plotpath=None, colormap="jet"):
    """Plot spectrogram."""
    sshow, freq = logscale_spec(
        audio.time_freq, factor=1.0, sr=audio.samplerate)
    ims = 20. * np.log10((np.abs(sshow)) / 10e-6)  # amplitude to decibel

    timebins, freqbins = np.shape(ims)

    plt.figure(figsize=(15, 7.5))
    plt.imshow(
        np.transpose(ims),
        origin="lower",
        aspect="auto",
        cmap=colormap,
        interpolation="none")
    plt.colorbar()

    plt.xlabel("time (s)")
    plt.ylabel("frequency (hz)")
    plt.xlim([0, timebins - 1])
    plt.ylim([0, freqbins])

    xlocs = np.float32(np.linspace(0, timebins - 1, 5))
    plt.xticks(xlocs, [
        "%.02f" % l for l in ((xlocs * len(audio.samples) / timebins) +
                              (0.5 * audio.binsize)) / audio.samplerate
    ])
    ylocs = np.int16(np.round(np.linspace(0, freqbins - 1, 10)))
    plt.yticks(ylocs, ["%.02f" % freq[i] for i in ylocs])

    if plotpath:
        plt.savefig(plotpath, bbox_inches="tight")
    else:
        plt.show()
