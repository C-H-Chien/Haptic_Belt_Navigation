'''
The purpose of this script is to analyze data after running test1.py
Data from test1.py is directly loaded into this script.
'''

# Import statements
import numpy as np
from matplotlib import pyplot as plt
import os

# Loads data [dirs, positions, times]
################################################################################
os.chdir('12MotorDirect_A')
actual_positions = np.load('dirs1.npy')
guessed_positions = np.load('positions1.npy')
actual_positions = np.append(np.load('dirs2.npy'), actual_positions)
guessed_positions = np.append(np.load('positions2.npy'), guessed_positions)
################################################################################

# Extracts x and y coordinates from the positional data
xs = guessed_positions[::2] ; ys = guessed_positions[1::2]
xs = [x - 360 for x in xs] ; ys = [-y + 360 for y in ys]

# Converts from x-y coordinate system to r-theta coordinate system
rs = [np.sqrt(x**2 + y**2) for (x,y) in zip(xs, ys)]
thetas = [np.arctan2(y,x) for (x,y) in zip(xs, ys)]

# Sets up plot parameters and pre-processing
colors = np.array([[255,0,0],[0,255,0],[0,0,255],[0,0,0],[80,0,200],
[200,0,80],[100,100,100],[180,120,40],[50,150,50]]) / 255
legend = ['N','NE','E','SE','S','SW','W','NW','STOP']
color_index = [] ; legend_index = []
for dir in actual_positions:
    color_index.append(colors[int(dir)])
    legend_index.append(legend[int(dir)])
fig = plt.figure()
ax = fig.add_subplot(111, projection='polar')
ax.set_yticklabels([])
ax.set_theta_zero_location('E')

# Plots the data
for i in range(len(thetas)):
    ax.scatter(thetas[i], rs[i], color=color_index[i], label=legend_index[i])
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.title('Trial 1: Direct Vibrotactile Cues')
plt.legend(by_label.values(), by_label.keys(), loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=5)
plt.show()
