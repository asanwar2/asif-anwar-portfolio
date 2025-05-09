# Subcritical Pile

This project involved modeling and characterizing the behavior of the Purdue University subcritical pile

## Project Overview
- Investigated neutron multiplication in the Purdue subcritical assembly
- Analyzed the influence of source strength, material configuration, and moderation
- Prepared a technical report summarizing experimental setup and theoretical models

## Folder Contents
- `codes`: MATLAB codes that generate heatmaps
- `data`: Raw or processed data used in the project
- `paper`: Final paper 

# Subcritical Pile – Radiation Dose Mapping (MATLAB)

This folder contains the MATLAB scripts used to generate radiation dose rate maps for the Purdue subcritical pile. 

---

## Script Overview

| File Name                                               | Description                                               |
|----------------------------------------------------------|-----------------------------------------------------------|
| `Radiation_Map_Subcrit_Room_gamma_doserate.m`           | Calculates gamma dose rate distribution in the room      |
| `Radiation_Map_Subcrit_Room_neutron_doserate.m`         | Calculates neutron dose rate distribution                |
| `Radiation_Map_Subcrit_Room_total_doserate.m`           | Combines neutron + gamma dose into total dose rate map   |

Each script creates a spatial map of radiation dose within the room and generates heatmap visualization.

---


## How to Run (MATLAB)

1. Open any of the `.m` files in MATLAB.
2. Make sure data points or mesh settings are defined at the top of each script.
3. Run:
```matlab
run('Radiation_Map_Subcrit_Room_gamma_doserate.m')
```
