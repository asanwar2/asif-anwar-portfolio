# Visualization of Neutron Flux Distribution in the PUR-1 Reactor

This project, completed for the Intro to Scientific Visualization graduate course, focused on transforming high-volume MCNP output data into visualizations of neutron flux distributions in the PUR-1 research reactor. The project aimed to bridge the gap between raw simulation output and intuitive understanding, making nuclear data accessible to both students and operators.


## Objective
To create accurate and engaging visual models of thermal, epithermal, and fast neutron flux within the reactor core, based on detailed MCNP simulations.

## 🧰 Tools & Methods
- MCNP6 (data source)
- Python
  - 3D visualizations for spatial flux distribution
- Cutaway and volume views to show internal flux gradients

## 📁 Contents
- `neutron-flux-visualization_PUR1.docx`: Final report summarizing goals, MCNP setup, visualization methods, and educational outcomes
- 'codes': Python codes for each energy region and cutaway chunks 

## Challenges Addressed
- Handling 20M+ row MCNP output file
- Visualizing multigroup flux in 3D space
- Communicating technical data for both educational and operational use

## Future Work
- Add isosurface rendering for improved 3D fidelity
- Explore GUI and interactive elements
- Consider AR/VR applications for immersive learning
