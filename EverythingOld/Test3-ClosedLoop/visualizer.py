from pylab import *
import numpy as np
from scipy.interpolate import griddata
from matplotlib import pyplot as plt
from matplotlib import animation
import time

# Defines the motors to fire for each of the cardinal directions
# 0: N | 1: NE | 2: E | 3: SE | 4: S | 5: SW | 6: W | 7: NW | 8: STOP
motors = {} ; motors[8] = {} ; motors[12] = {}
motors[8][2] = [0] ; motors[8][3] = [1]
motors[8][4] = [2] ; motors[8][5] = [3]
motors[8][6] = [4] ; motors[8][7] = [5]
motors[8][8] = [6] ; motors[8][1] = [7]
# motors[8][8] = [1,2,3,4,5,6,7,8]
motors[12][10] = [0] ; motors[12][11] = [1]
motors[12][12] = [2] ; motors[12][13] = [3]
motors[12][2] = [4] ; motors[12][3] = [5]
motors[12][4] = [6] ; motors[12][5] = [7]
motors[12][6] = [8] ; motors[12][7] = [9]
motors[12][8] = [10] ; motors[12][9] = [11]
# motors[12][12] = [2,3,4,5,6,7,8,9,10,11,12,13]

start = time.time()

#create 5000 Random points distributed within the circle radius 100
def gen_data(numMotors, max_r, max_theta):
    file = open('motors.txt', 'r')
    motorsToFire = file.readline().split('|')[:-1]
    intensities = file.readline().split('|')[:-1]
    adjust = (np.pi / (1.5*numMotors))
    angle_points = np.linspace(-adjust, 2*np.pi-adjust, numMotors)
    radial_points = [1.0 for i in range(numMotors)]
    points = np.transpose([radial_points, angle_points])
    values = np.ones(numMotors)
    for i in range(len(motorsToFire)):
        values[motors[numMotors][int(motorsToFire[i])][0]] = intensities[i]
    return points, values

def update_plot(num, start, theta, r, ax1, data):
    if time.time() - start > 1:
        points, values = gen_data(numMotors, max_r, max_theta)
        data = griddata(points, values, (grid_r, grid_theta), method='nearest', fill_value=0)
        start = time.time()
        ax1.pcolormesh(theta, r, data.T)

numMotors = 12 ; max_r = 1 ; max_theta = (2.0 * np.pi)
theta = np.linspace(0, max_theta, num=100)
r = np.linspace(0 ,max_r, 100)
grid_r, grid_theta = np.meshgrid(r, theta)
points, values = gen_data(numMotors, max_r, max_theta)
data = griddata(points, values, (grid_r, grid_theta), method='nearest')

fig = plt.figure()

#Create a polar projection
ax1 = plt.subplot(projection="polar")

line_ani = animation.FuncAnimation(
    fig, update_plot, 25, fargs=(start, theta, r, ax1, data), interval=100)
fig.colorbar(ax1.pcolormesh(theta, r, data.T))
plt.show()
