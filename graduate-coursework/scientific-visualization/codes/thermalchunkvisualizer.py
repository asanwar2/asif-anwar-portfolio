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
df = pd.read_csv('C:/Users/asanw/OneDrive/Desktop/CS 530/Final Project/meshtal_final.txt', sep='\s+', names=column_names, skiprows=skip_rows)  # Replace n with the number of rows to skip

# Prepare the data
# Convert to appropriate data types if necessary
df['Result'] = df['Result'].astype(float)

# Filter to get only the bottom half of the removed quadrant
# This will be where X is positive and Y is negative
bottom_half_df = df[(df['X'] > 0) & (df['Y'] < 0)]

# Normalize the 'Result' values for the bottom half
result_normalized_bottom_half = (bottom_half_df['Result'] - bottom_half_df['Result'].min()) / (bottom_half_df['Result'].max() - bottom_half_df['Result'].min())

# Create a new 3D scatter plot for the bottom half
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Scatter plot for the bottom half using 'Result' to determine point color
# Adjust the sizes if needed
sc = ax.scatter(bottom_half_df['X'], bottom_half_df['Y'], bottom_half_df['Z'], c=bottom_half_df['Result'], s=result_normalized_bottom_half * 100, cmap='hot', alpha=0.6)

# Color bar indicating the scale of neutron flux
cbar = plt.colorbar(sc)
cbar.set_label('Neutron Flux (n/cm^2/s per neutron in the core)')

# Set labels and title for the bottom half plot
ax.set_xlabel('X Coordinate')
ax.set_ylabel('Y Coordinate')
ax.set_zlabel('Z Coordinate')
plt.title('Thermal Neutron Flux Distribution Bottom Half Cutaway View in PUR-1 Reactor Core')

# Show the plot for the bottom half
plt.show()

# Filter out the quarter with positive X and Y values for the cutaway
#cutaway_df = df[~((df['X'] > 0) & (df['Y'] > 0))]

# Normalize the 'Result' values to use as point sizes (optional)
#result_normalized_cutaway = (cutaway_df['Result'] - cutaway_df['Result'].min()) / (cutaway_df['Result'].max() - cutaway_df['Result'].min())

# Create a 3D scatter plot using the cutaway DataFrame
#fig = plt.figure(figsize=(10, 8))
#ax = fig.add_subplot(111, projection='3d')

# Scatter plot using 'Result' to determine point color
# Multiply 'result_normalized_cutaway' to scale up the sizes for visibility
#sc = ax.scatter(cutaway_df['X'], cutaway_df['Y'], cutaway_df['Z'], c=cutaway_df['Result'], s=result_normalized_cutaway * 100, cmap='hot', alpha=0.6)

# Color bar indicating the scale of neutron flux
#cbar = plt.colorbar(sc)
#cbar.set_label('Neutron Flux (n/cm^2/s per neutron in the core)')

# Set labels and title
#ax.set_xlabel('X Coordinate')
#ax.set_ylabel('Y Coordinate')
#ax.set_zlabel('Z Coordinate')
#plt.title('Thermal Neutron Flux Distribution Cutaway View in PUR-1 Reactor Core')

# Show the plot
#plt.show()

# Normalize the 'Result' values to use as point sizes (optional)
#result_normalized = (df['Result'] - df['Result'].min()) / (df['Result'].max() - df['Result'].min())

# Create a 3D scatter plot
#fig = plt.figure(figsize=(10, 8))
#ax = fig.add_subplot(111, projection='3d')

# Scatter plot using 'Result' to determine point color
# Multiply 'result_normalized' to scale up the sizes for visibility
#sc = ax.scatter(df['X'], df['Y'], df['Z'], c=df['Result'], s=result_normalized * 100, cmap='hot', alpha=0.6)

# Color bar indicating the scale of neutron flux
#cbar = plt.colorbar(sc)
#cbar.set_label('Neutron Flux (n/cm^s/s per neutron in the core)')

# Set labels and title
#ax.set_xlabel('X Coordinate')
#ax.set_ylabel('Y Coordinate')
#ax.set_zlabel('Z Coordinate')
#plt.title('Thermal Neutron Flux Distribution in PUR-1 Reactor Core')

# Show the plot
#plt.show()
