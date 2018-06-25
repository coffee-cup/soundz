import numpy as np
from matplotlib import pyplot as plt
from scipy import signal
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (generate_binary_structure,
                                      iterate_structure, binary_erosion)
from utils import log
from fingerprint import Fingerprint


def preprocess(samples, sr):
    """Preprocess audio preparing it for the spectrogram creation."""

    # Convert to mono signal
    samples = samples.sum(axis=1) / 2

    # Remove DC bias by subtracting the mean
    # samples = samples - np.mean(samples)

    # Downsample to save space and processing
    # secs = len(samples) / sr
    # samps = secs * 8000
    # samples = signal.resample(samples, samps)

    return samples


def find_peaks(spec):
    """Finds peaks of audio object spectrogram."""

    peak_neighbourhood_size = 15
    min_amp = 10

    struct = generate_binary_structure(2, 1)
    neighborhood = iterate_structure(struct, peak_neighbourhood_size)

    # find local maxima using filter shape
    local_max = maximum_filter(spec, footprint=neighborhood) == spec
    background = (spec == 0)
    eroded_background = binary_erosion(
        background, structure=neighborhood, border_value=1)

    # boolean mask with True at peaks
    detected_peaks = local_max ^ eroded_background

    # extract peaks
    amps = spec[detected_peaks]
    j, i = np.where(detected_peaks)

    # filter peaks so amplitude is greater than min_amp
    amps = amps.flatten()
    peaks = zip(i, j, amps)

    # freq, time, amp
    peaks_filtered = [x for x in peaks if x[2] > min_amp]

    # get indices for frequency and time
    frequency_idx = [x[1] for x in peaks_filtered]
    time_idx = [x[0] for x in peaks_filtered]

    return (frequency_idx, time_idx)


def plot_spectrogram(ax, freqs, times, spec):
    """Plots spectrogram."""
    ax.set_title('Spectrogram')
    ax.set_xlabel('Time [sec]')
    ax.set_ylabel('Frequency [Hz]')
    ax.pcolormesh(times, freqs, spec, cmap='jet')


def plot_constellation(ax, time_idx, freq_idx):
    """Plots constellation map."""
    ax.set_title('Constellation Map')
    ax.set_ylabel('Frequency')
    ax.scatter(time_idx, freq_idx, s=1, c='b', marker='.')


def create_plots(title, freqs, times, spec, time_idx, freq_idx):
    """Plots both the spectrogram and constellation map."""
    fig = plt.figure(figsize=(15, 7.5))
    ax1 = plt.subplot(2, 1, 1)
    ax2 = plt.subplot(2, 1, 2)

    plt.suptitle(title)

    plot_constellation(ax1, time_idx, freq_idx)
    plot_spectrogram(ax2, freqs, times, spec)

    plt.show()


def generate_fingerprints(title, samples, sr=44100, plot=False):
    """
    Creates fingerprints for provided samples.

    Returns: List of fingerprint objects
    """
    frame_size = 1024
    window = 'hamming'
    overlap = np.floor(0.5 * frame_size)
    nfft = frame_size
    scaling = 'spectrum'

    log('Sample rate: {}'.format(sr))
    log('Length: {:.2f} sec'.format(samples.shape[0] / sr))
    log('Window size: {:.2f} ms'.format(frame_size / sr * 1000))
    log('')

    log('Creating spectrogram...')
    freqs, times, spec = signal.spectrogram(
        samples,
        sr,
        window=window,
        nperseg=frame_size,
        noverlap=overlap,
        nfft=nfft,
        scaling=scaling)

    # Apply log transform
    spec = 10 * np.log10(spec)
    spec[spec == -np.inf] = 0

    log('Finding peaks...')
    freq_idx, time_idx = find_peaks(spec)
    peaks = zip(freq_idx, time_idx)
    log('{} peaks'.format(len(freq_idx)))

    log('Creating fingerprints...')
    prints = create_fingerprints(peaks)
    log('{} fingerprints'.format(len(prints)))

    if plot:
        log('Plotting...')
        create_plots(title, freqs, times, spec, time_idx, freq_idx)

    return prints


def create_fingerprints(peaks, fan_value=15):
    """
    Create fingerprints for all the peaks.
    fingerprint = hash:time
    hash        = (f1, f2, t2 - t1)
    time        = t1
    """
    prints = []
    peaks = list(peaks)
    for i in range(len(peaks)):
        for j in range(1, fan_value):
            if (i + j) < len(peaks):
                f1 = peaks[i][0]
                f2 = peaks[i + j][0]
                t1 = peaks[i][1]
                t2 = peaks[i + j][1]
                t_delta = t2 - t1

                # Hashes must be within 200s of each other
                if t_delta >= 0 and t_delta <= 200:
                    h = '{},{},{}'.format(f1, f2, t_delta)
                    p = Fingerprint(h, t1)
                    prints.append(p)

    return list(set(prints))
