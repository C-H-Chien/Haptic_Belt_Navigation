'''
The purpose of this script is to analyze data after running test2.py
Data from test2.py is directly loaded into this script
'''

# Import statements
import numpy as np
from matplotlib import pyplot as plt
import os

# Loads data [dirs, positions, times]
################################################################################
os.chdir('12MotorGaussian_A')
actual_positions = np.load('test2dirs.npy')
guessed_positions = np.load('test2positions.npy')
times = np.load('test2times.npy')

os.chdir('../12MotorGaussian_B')
actual_positions = np.append(np.load('test2dirs.npy'), actual_positions)
guessed_positions = np.append(np.load('test2positions.npy'), guessed_positions)
times = np.append(np.load('test2times.npy'), times)

os.chdir('../12MotorGaussian_C')
actual_positions = np.append(np.load('test2dirs.npy'), actual_positions)
guessed_positions = np.append(np.load('test2positions.npy'), guessed_positions)
times = np.append(np.load('test2times.npy'), times)

################################################################################

# Extracts x and y coordinates from the positional data
xs = guessed_positions[::2] ; ys = guessed_positions[1::2]
xs = [x-360 for x in xs] ; ys = [-y + 360 for y in ys]

# Converts fro mx-y coordinate system to r-theta coordinate system
rs = [np.sqrt(x**2 + y**2) for (x,y) in zip(xs, ys)]
thetas = [np.arctan2(y,x) for (x,y) in zip(xs, ys)]

for i in range(len(thetas)):
    if thetas[i] < 0:
        thetas[i] = 360 + (180 / np.pi) * thetas[i]
    else:
        thetas[i] = (180 / np.pi) * thetas[i]

# Calculates errors between actual and clicked positions
errors = []
for i in range(len(thetas)):
    if abs(thetas[i] - actual_positions[i]) > 180:
        error = 360 - abs(actual_positions[i] - thetas[i])
    else:
        error = abs(actual_positions[i] - thetas[i])
    errors.append(error)

print("Median Error: {}".format(str(np.median(errors))))
print("Mean Error: {}".format(str(np.mean(errors))))

# Sets up plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='polar')
ax.set_yticklabels([])
ax.set_theta_zero_location('E')
c = errors
plt.scatter(thetas, rs, c=c, cmap = 'RdYlGn_r')
cbar = plt.colorbar()
cbar.set_label('Error Magnitude')
plt.title('12-Motor Belt: Gaussian Vibration Cues')
plt.show()
