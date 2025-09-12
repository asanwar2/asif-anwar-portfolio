# Visualization of Neutron Flux Distribution in the PUR-1 Reactor

This project, completed for the Intro to Scientific Visualization graduate course, focused on transforming high-volume MCNP output data into visualizations of neutron flux distributions in the PUR-1 research reactor. The project aimed to bridge the gap between raw simulation output and intuitive understanding, making nuclear data accessible to both students and operators.

# Neutron Flux Visualization Scripts – PUR-1 Reactor

The folder contains Python scripts developed for visualizing MCNP-simulated neutron flux data from the PUR-1 reactor core. Each script is tailored to a specific neutron energy group (thermal, epithermal, fast) and visualization mode (core view or cutaway chunk view). Large simulation outputs (20M+ data points) were translated into 3D visualizations to support operational insight and nuclear education.

## Project Objectives

- Visualize thermal, epithermal, and fast neutron flux from MCNP6 simulations
- Transform raw tally data into intuitive heatmaps and 3D spatial maps
- Make neutron distributions accessible to students, operators, and educators

---

## Project Structure

| Folder/File                         | Purpose                                              |
|------------------------------------|------------------------------------------------------|
| `codes/`                           | Python scripts for flux rendering (core & cutaway)  |
| `neutron-flux-visualization.docx`  | Final report detailing data, methods, and insights  |

## Contents
- `neutron-flux-visualization_PUR1.docx`: Final report summarizing goals, MCNP setup, visualization methods, and educational outcomes
- 'codes': Python codes for each energy region and cutaway chunks
- 
## File Descriptions

- `thermalcorevisualizer.py`  
  Visualizes the full core distribution of thermal neutron flux.

- `thermalchunkvisualizer.py`  
  Visualizes thermal neutron flux with a cutaway (chunk removed) to reveal interior distribution.

- `epithermalcorevisualizer.py`  
  Displays epithermal neutron flux across the entire core.

- `epithermalchunkvisualizer.py`  
  Displays epithermal neutron flux with internal cutaway for better spatial insight.

- `fastneutroncorevisualizer.py`  
  Full core visualization of fast neutron flux.

- `fastneutronchunkvisualizer.py`  
  Fast neutron flux visualization with a core chunk removed.

- `totalfluxvisualizer.py`  
  Aggregates thermal, epithermal, and fast flux into one visualization.

How to Run the Code
1. Install Python and dependencies
2. Load your mesh tally flux data as .txt or .csv
3. Run a visualizer script:
   python thermalcorevisualizer.py
   
> ⚠️ Note: The original version of this script was used to analyze MCNP output. Due to export control concerns, this version uses synthetic input and is intended for educational demonstration only.


Each script:
- Reads spatial + flux values
- Builds a mesh grid
- Uses matplotlib to plot 3D voxel maps

## Objective
To create accurate and engaging visual models of thermal, epithermal, and fast neutron flux within the reactor core, based on detailed MCNP simulations.

## Tools & Methods
- MCNP6
- Python
  - 3D visualizations for spatial flux distribution
- Cutaway and volume views to show internal flux gradients


## Challenges Addressed
- Handling 20M+ row MCNP output file
- Visualizing multigroup flux in 3D space
- Communicating technical data for both educational and operational use

## Future Work
- Add isosurface rendering for improved 3D fidelity
- Explore GUI and interactive elements
- Consider AR/VR applications for immersive learning
