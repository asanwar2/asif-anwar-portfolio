# Virtual Lab for Nuclear Engineering Education

This project was developed as part of my undergraduate research where I designed MATLAB-based virtual laboratory environment that helps students understand key nuclear engineering concepts through simulation and visualization. It serves both as a teaching tool and a simulation benchmark.

---

## Project Objectives

- Provide an accessible, simulation-based alternative to hands-on reactor experiments
- Offer simplified, interactive tools for spectrum generation and interpretation
- Enable students to visualize phenomena like thermal feedback and delayed neutron behavior

---

## Project Structure

| Folder/File                  | Description                                                  |
|-----------------------------|--------------------------------------------------------------|
| `codes`                   | Contains simulation and visualization code                   |
| `paper`                 | Final research paper outlining objectives, implementation, and educational impact |
| `cs_spectrum.m`             | MATLAB benchmark spectrum generator for Cs-137               |

## Purpose

- Demonstrate gamma emission energy signatures from Cs-137
- Model spectrum shape with basic statistical noise and resolution

This script:
- Generates a benchmark gamma-ray energy spectrum for Cs-137 
- Adds Gaussian broadening to simulate detector resolution
- Plots the resulting spectrum with labels for photopeak and Compton edge
- Simulate energy resolution and detector response
- Serve as a reference for validating simulations or other virtual spectra


## How to Run (MATLAB)

1. Open `cs_spectrum.m` in MATLAB.
2. Simply click **"Run"**, or type:
```matlab
run('cs_spectrum.m')
```

The script will:
- Generate an energy array (e.g., 0–1000 keV)
- Display a labeled spectrum plot
- A Gaussian-shaped photopeak centered at 662 keV
- Optional statistical noise
- Features like Compton edge

---

No external data files are required — everything is internally generated.

Customization Options
- Energy Range: Adjust E_min and E_max variables
- Detector Resolution: Modify FWHM or sigma settings
- Peak Position/Width: Customize to match different isotopes
