# Neutron Flux Visualization Scripts – PUR-1 Reactor

This folder contains Python scripts developed for visualizing MCNP-simulated neutron flux data from the PUR-1 reactor core. Each script is tailored to a specific neutron energy group (thermal, epithermal, fast) and visualization mode (core view or cutaway chunk view). Large simulation outputs (20M+ data points) were translated into 3D visualizations to support operational insight and nuclear education.

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
| `images/`                          | Saved plots and screenshots                         |


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
1. Install Python and dependencies (see below)
2. Load your mesh tally flux data as .txt or .csv
3. Run a visualizer script:
   python thermalcorevisualizer.py

Each script:
- Reads spatial + flux values
- Builds a mesh grid
- Uses matplotlib to plot 3D voxel maps

