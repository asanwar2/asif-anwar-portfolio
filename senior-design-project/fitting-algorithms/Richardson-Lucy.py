import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.signal import deconvolve

# Load data from txt file
data = np.loadtxt('ApolloCo60.txt', delimiter='\t')

# Extract energy column
energy = data[:, 1]

# Smoothing filter
window_size = 15
energy_smooth = np.convolve(energy, np.ones(window_size)/window_size, mode='same')

# Identify peaks
peak_locs, _ = find_peaks(energy_smooth, prominence=50, distance=10)

# Deconvolution
kernel = np.array([1, 0, -1])
peak_deconv = []
for c in peak_locs:
    peak, _ = deconvolve(energy_smooth[c-10:c+10], kernel)
    peak_deconv.append(peak)

# Plot spectrum with identified peaks and deconvolved peaks
plt.plot(energy, label='Spectrum')
for c, p in zip(peak_locs, peak_deconv):
    plt.plot(np.arange(c-10, c+10), p, label='Peak at %.1f keV' % energy[c])
plt.xlabel('Channel Number')
plt.ylabel('Energy (keV)')
plt.legend()
plt.show()
