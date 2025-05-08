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
- scikit-learn (
