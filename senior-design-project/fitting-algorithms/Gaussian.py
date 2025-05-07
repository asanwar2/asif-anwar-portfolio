import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Load data from txt file
data = np.loadtxt('ApolloCo60.txt', delimiter='\t')

# Extract energy column
energy = data[:, 1]

# Smoothing filter
window_size = 15
energy_smooth = np.convolve(energy, np.ones(window_size)/window_size, mode='same')

# Second derivative
diff2 = np.diff(np.diff(energy_smooth))

# Peak locations
peak_locs = np.where(diff2 < 0)[0] + 1

# Identify peaks
exclude = 2
bounds = np.logical_and(peak_locs > exclude, peak_locs < len(energy) - exclude)
channel = peak_locs[bounds][np.argsort(diff2[peak_locs][bounds])[-9:]]
peak_energies = energy[channel]

# Gaussian fitting
def gaussian(x, a, x0, sigma):
    return a * np.exp(-(x - x0)**2 / (2 * sigma**2))

peak_intensities = []
peak_widths = []
for c in channel:
    p0 = [energy[c], energy[c], 10] # initial guesses for parameters
    popt, pcov = curve_fit(gaussian, energy_smooth[c-10:c+10], energy[c-10:c+10], p0=p0)
    peak_intensities.append(popt[0])
    peak_widths.append(popt[2])

# Plot spectrum with identified peaks and Gaussian fits
plt.plot(energy, label='Spectrum')
for c, e, i, w in zip(channel, peak_energies, peak_intensities, peak_widths):
    plt.plot(energy_smooth[c-10:c+10], gaussian(energy_smooth[c-10:c+10], i, e, w), label='Peak at %.1f keV' % e)
plt.xlabel('Channel Number')
plt.ylabel('Energy (keV)')
plt.legend()
plt.show()
