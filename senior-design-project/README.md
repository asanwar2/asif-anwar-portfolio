# Senior Design Project – Radioisotope Identification

This senior design project, sponsored by H3D Gamma Inc., focused on designing and optimizing a radioisotope identification code for use in portable gamma-ray detectors. We combined MCNP simulations with machine learning techniques to develop a real-time identification system that meets ANSI N42.34 performance standards.

## Project Summary
- Simulated gamma-ray spectra using MCNP for various radionuclides and detector geometries (HPGe, NaI, CZT)
- Developed Python-based algorithms for peak identification and classification
- Applied Random Forest classifiers to match unknown spectra to known isotopes
- Evaluated accuracy against ANSI standards and unknown test sources

## Folder Contents
- `fitting-algorithms/`: Python scripts used for spectrum processing and isotope prediction
- `radioisotope-identification_H3D.pdf`: Final design report documenting methodology, simulation setup, ML models, and results

> ⚠️ Note: The original version of this script was used to analyze MCNP output. Due to export control concerns, this version uses synthetic input and is intended for educational demonstration only.

# Fitting Algorithms – Radioisotope Spectra Processing

These scripts support the senior design project on radioisotope identification. They perform curve fitting and feature extraction on simulated gamma spectra to prepare inputs for classification models.

## File Overview

| File Name                | Function                                         |
| ------------------------ | ------------------------------------------------ |
| `Gaussian.py`            | Fit spectrum using Gaussian profile              |
| `Lorentzian.py`          | Fit spectrum using Lorentzian profile            |
| `Voigt.py`               | Use Voigt function for hybrid peak shape fitting |
| `Richardson-Lucy.py`     | Apply deconvolution for resolution correction    |
| `simulated_spectrum.csv` | Sample input spectrum file (if included)         |


## Functions
- Peak smoothing and denoising using Savitzky-Golay filter
- Second derivative method for peak detection
- Curve fitting (Gaussian, Lorentzian, Voigt profiles) to extract peak positions and intensities
- Exporting feature vectors for machine learning

## Tools Used
- Python
- NumPy, SciPy
- Matplotlib
- scikit-learn

## Tools & Technologies
- **MCNP** for gamma-ray transport and detector modeling
- **Python**, **NumPy**, **SciPy**, **scikit-learn**
- Spectral analysis: Savitzky-Golay filter, second-derivative method
- Random Forest for classification
