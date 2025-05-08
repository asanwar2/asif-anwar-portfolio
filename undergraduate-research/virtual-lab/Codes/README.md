## Purpose

- Demonstrate gamma emission energy signatures from Cs-137
- Model spectrum shape with basic statistical noise and resolution

This script:
- Generates a synthetic Cs-137 energy spectrum
- Adds Gaussian broadening to simulate detector resolution
- Plots the resulting spectrum with labels for photopeak and Compton edge

## How to Run (MATLAB)

1. Open `cs_spectrum.m` in MATLAB.
2. Simply click **"Run"**, or type:
```matlab
run('cs_spectrum.m')
```
The script will:
- Generate an energy array (e.g., 0–1000 keV)
- Simulate counts with a peak at 662 keV
- Display a labeled spectrum plot
No external data files are required — everything is internally generated.

Customization Options
Energy Range: Adjust E_min and E_max variables
Detector Resolution: Modify FWHM or sigma settings
Peak Position/Width: Customize to match different isotopes
