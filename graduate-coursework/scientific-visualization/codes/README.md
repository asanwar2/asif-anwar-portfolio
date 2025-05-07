# Neutron Flux Visualization Scripts – PUR-1 Reactor

This folder contains Python scripts developed for visualizing MCNP-simulated neutron flux data from the PUR-1 reactor core. Each script is tailored to a specific neutron energy group (thermal, epithermal, fast) and visualization mode (core view or cutaway chunk view).

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

