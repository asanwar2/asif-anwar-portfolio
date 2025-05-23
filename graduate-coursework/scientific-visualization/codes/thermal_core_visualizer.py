import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load the data
# Define ranges
range1 = list(range(0, 5993871))  # Skips rows 1-5993870
range2 = list(range(8990798, 11987727))  # Skips rows 8990799-11987726


# Combine the ranges
skip_rows = range1 + range2

column_names = ['Energy', 'X', 'Y', 'Z', 'Result', 'Rel_Error', ...]  # Add all needed column names
df = pd.read_csv('../data/meshtal_final.txt', sep='\s+', names=column_names, skiprows=skip_rows)  # Replace n with the number of rows to skip

# Prepare the data
# Convert to appropriate data types if necessary
df['Result'] = df['Result'].astype(float)

# Normalize the 'Result' values to use as point sizes (optional)
result_normalized = (df['Result'] - df['Result'].min()) / (df['Result'].max() - df['Result'].min())

# Create a 3D scatter plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Scatter plot using 'Result' to determine point color
# Multiply 'result_normalized' to scale up the sizes for visibility
sc = ax.scatter(df['X'], df['Y'], df['Z'], c=df['Result'], s=result_normalized * 100, cmap='hot', alpha=0.6)

# Color bar indicating the scale of neutron flux
cbar = plt.colorbar(sc)
cbar.set_label('Neutron Flux (n/cm^s/s per neutron in the core)')

# Set labels and title
ax.set_xlabel('X Coordinate')
ax.set_ylabel('Y Coordinate')
ax.set_zlabel('Z Coordinate')
plt.title('Thermal Neutron Flux Distribution in PUR-1 Reactor Core')

# Show the plot
plt.show()
