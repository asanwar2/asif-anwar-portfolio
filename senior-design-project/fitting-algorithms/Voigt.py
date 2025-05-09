import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.special import wofz

# Load data from txt file
data = np.loadtxt('../data/ApolloCo60.txt', delimiter='\t')

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

# Voigt fitting
def voigt(x, a, x0, sigma, gamma):
    z = ((x - x0) + 1j*gamma) / (sigma * np.sqrt(2))
    return a * np.real(wofz(z))

peak_intensities = []
peak_positions = []
peak_widths = []
peak_gammas = []
for c in channel:
    p0 = [energy[c], 10, 10, 10] # initial guesses for parameters
    popt, pcov = curve_fit(voigt, energy_smooth[c-10:c+10], energy[c-10:c+10], p0=p0)
    peak_intensities.append(popt[0])
    peak_positions.append(popt[1])
    peak_widths.append(popt[2])
    peak_gammas.append(popt[3])

# Plot spectrum with identified peaks and Voigt fits
plt.plot(energy, label='Spectrum')
for c, e, i, w, g in zip(channel, peak_energies, peak_intensities, peak_widths, peak_gammas):
    plt.plot(energy_smooth[c-10:c+10], voigt(energy_smooth[c-10:c+10], i, e, w, g), label='Peak at %.1f keV' % e)
plt.xlabel('Channel Number')
plt.ylabel('Energy (keV)')
plt.legend()
plt.show()
