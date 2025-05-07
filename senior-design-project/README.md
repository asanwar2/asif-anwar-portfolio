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


## Tools & Technologies
- **MCNP** for gamma-ray transport and detector modeling
- **Python**, **NumPy**, **SciPy**, **scikit-learn**
- Spectral analysis: Savitzky-Golay filter, second-derivative method
- Random Forest for classification
