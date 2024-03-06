'''
The purpose of this script is to analyze data after running Closed
Loop tests for different maps
'''

# Import statements
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.font_manager import FontProperties
import os, math

def get_idealPath(i, j, data, orientations ,thresh):
    positions = data[i][j] ; xs = positions[::3] ; zs = positions[2::3]
    thetas = orientations[i][j]
    directions = [] ; finished = 1

    # These are the waypoints of the maze task
    ############################################################################
    waypoints = {}
    waypoints[-1] = [0.0, 0.0, 0.0]
    waypoints[0] = [0.0, 0.0, 0.0]
    waypoints[1] = [7.5, 0.0, 0.0] ; waypoints[2] = [7.5, 0.0, 4.0]
    waypoints[3] = [0.25, 0.0, 4.0] ; waypoints[4] = [7.5, 0.0, 4.0] ; waypoints[5] = [7.5, 0, -4.0]
    waypoints[6] = [11.5, 0.0, -4.0] ; waypoints[7] = [11.5, 0.0, 4.5]
    waypoints[8] = [11.5, 0.0, 4.5]
    ############################################################################

    # These are the waypoints of the wayfinding task (same as open loop)
    ############################################################################
    # waypoints[-1] = [0.0, 0.0, 0.0]
    # waypoints[0] = [0.0, 0.0, 0.0]
    # waypoints[1] = [6.0, 0.0, 4.0] ; waypoints[2] = [2.0, 0.0, 9.0]
    # waypoints[3] = [-5.0, 0.0, 9.0] ; waypoints[4] = [-4.0, 0.0, 3.0]
    # waypoints[5] = [-7.0, 0.0, -6.0] ; waypoints[6] = [4.0, 0.0, -4.0]
    # waypoints[7] = [0.0, 0.0, 0.0] ; waypoints[8] = [0.0, 0.0, 0.0]
    ############################################################################

    distances_ = []
    for (x, z, theta) in zip(xs, zs, thetas):
        curPos = (x,z)
        dx = waypoints[finished][0] - curPos[0]
        dz = waypoints[finished][2] - curPos[1]
        desiredAngle = math.atan2(dx, dz) * (180.0 / math.pi)
        angleError = theta - desiredAngle
        distToDest = np.sqrt((curPos[0] - waypoints[finished-1][0])**2 + (curPos[1] - waypoints[finished-1][2])**2)

        distances_.append(getDistance(curPos[0], curPos[1], waypoints[finished-1][0], waypoints[finished-1][2], waypoints[finished-2][0], waypoints[finished-2][2]))
        if angleError > 180:
            angleError -= 360
        elif angleError < -180:
            angleError += 360

        if distToDest < thresh:
            finished += 1
        direction = desiredAngle
        if direction < 0:
            direction = 360 + direction
        directions.append(direction)
    if np.mean(distances_) > 5:
        print(distances_)
        plt.plot(xs, zs) ;
        currentAxis = plt.gca()
        currentAxis.add_patch(Rectangle((0, 3), 4, 4, alpha=1, fill=None))
        currentAxis.add_patch(Rectangle((-4, 7), 6, 1, alpha=1, fill=None))
        currentAxis.add_patch(Rectangle((-7, 1.5), 2, 5.5, alpha=1, fill=None))
        currentAxis.add_patch(Rectangle((-4, -4), 4, 3, alpha=1, fill=None))
        currentAxis.add_patch(Rectangle((2, -1), 2, 1, alpha=1, fill=None))
        currentAxis.add_patch(Circle((6, 4), radius=0.25, color='black'))
        currentAxis.add_patch(Circle((2, 9), radius=0.25, color='black'))
        currentAxis.add_patch(Circle((-5, 9), radius=0.25, color='black'))
        currentAxis.add_patch(Circle((-4, 3), radius=0.25, color='black'))
        currentAxis.add_patch(Circle((-7, -6), radius=0.25, color='black'))
        currentAxis.add_patch(Circle((4, -4), radius=0.25, color='black')) ; plt.show()
    return directions, distances_

def getDistance(x0, y0, x1, y1, x2, y2):
    numerator = abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1)
    denominator = np.sqrt((y2-y1)**2 + (x2-x1)**2)
    if denominator != 0:
        ans = float(numerator / denominator)
    else:
        ans = 0.0
    return ans

# These are the directories of the wayfinding task
############################################################################
# directories = ["Wayfinding Test 1_75", "Wayfinding Test 2_75", "Wayfinding Test 1_50", "Wayfinding Test 2_50"]
files = ['8Motor_positions_1D.npy', 'positions_1D.npy', 'positions_1C.npy']
directories = ["Maze Test 1", "Maze Test 2", "Maze Test 3"]
############################################################################

# These are the directories of the maze task
############################################################################
files = ['8Motor_positions_1B.npy', 'positions_1B.npy',
'positions_1A.npy']
labels = ['8 Motor Direct', '12 Motor Direct', '12 Motor Gaussian']
############################################################################

data = {}

for i in range(len(directories)):
    os.chdir(directories[i])
    data[i] = {}
    for j in range(len(files)):
        xs = np.array([]) ; zs = np.array([])
        load_data = np.load(files[j])
        data[i][j] = load_data
        xs = load_data[::3]
        zs = load_data[2::3]
        plt.plot(xs, zs, label=labels[j])

    currentAxis = plt.gca()
    # These are the obstacles of the maze task
    ############################################################################
    currentAxis.add_patch(Rectangle((-2, -1), 2, 6, alpha=1, fill=None))
    currentAxis.add_patch(Rectangle((0, 0), 4, 2, alpha=1, fill=None))
    currentAxis.add_patch(Rectangle((0, -7), 6, 6, alpha=1, fill=None))
    currentAxis.add_patch(Rectangle((6, -7), 8, 2, alpha=1, fill=None))
    currentAxis.add_patch(Rectangle((12, -5), 2, 10, alpha=1, fill=None))
    currentAxis.add_patch(Rectangle((9, -3), 2, 8, alpha=1, fill=None))
    currentAxis.add_patch(Rectangle((-2, 6), 16, 1, alpha=1, fill=None))
    currentAxis.add_patch(Circle((0.25, 4), radius=0.25, color='black'))
    currentAxis.add_patch(Circle((11.5, 4.5), radius=0.25, color='black'))
    ############################################################################

    # These are the obstacles of the wayfinding task
    ############################################################################
    currentAxis.add_patch(Rectangle((0, 3), 4, 4, alpha=1, fill=None))
    currentAxis.add_patch(Rectangle((-4, 7), 6, 1, alpha=1, fill=None))
    currentAxis.add_patch(Rectangle((-7, 1.5), 2, 5.5, alpha=1, fill=None))
    currentAxis.add_patch(Rectangle((-4, -4), 4, 3, alpha=1, fill=None))
    currentAxis.add_patch(Rectangle((2, -1), 2, 1, alpha=1, fill=None))
    currentAxis.add_patch(Circle((6, 4), radius=0.25, color='black'))
    currentAxis.add_patch(Circle((2, 9), radius=0.25, color='black'))
    currentAxis.add_patch(Circle((-5, 9), radius=0.25, color='black'))
    currentAxis.add_patch(Circle((-4, 3), radius=0.25, color='black'))
    currentAxis.add_patch(Circle((-7, -6), radius=0.25, color='black'))
    currentAxis.add_patch(Circle((4, -4), radius=0.25, color='black'))
    ############################################################################

    plt.title(directories[i])
    plt.xlim(-15, 15) ; plt.ylim(-10, 10)
    fontP = FontProperties() ; fontP.set_size('small')
    plt.legend(loc='upper right', bbox_to_anchor=(1.05, 1.05), prop=fontP)
    plt.show()
    os.chdir("..")
times = {} ; times[0] = [] ; times[1] = [] ; times[2] = []
for i in range(len(directories)):
    for j in range(len(files)):
        times[j].append(len(data[i][j]) / 3)
for i in times.keys():
    print("{} time is {}".format(str(i), str(np.mean(times[i]))))

orientations = {} ; accuracy = {} ; accuracy[0] = [] ; accuracy[1] = [] ; accuracy[2] = []
deviations = {} ; deviations[0] = [] ; deviations[1] = [] ; deviations[2] = []
distances = {} ; distances[0] = [] ; distances[1] = [] ; distances[2] = []
files = ['8Motor_orientations_1B.npy', 'orientations_1B.npy',
'orientations_1A.npy'] ; nums = [1,2,3,4]
for i in range(len(directories)):
    os.chdir(directories[i])
    orientations[i] = {}
    for j in range(len(files)):
        thetas = np.array([])
        load_data = np.load(files[j])
        orientations[i][j] = load_data[::3]
        thetas = orientations[i][j]
        ts = np.linspace(0, len(thetas) / 2, num=len(thetas))
        if i < 3:
            directions, distances_ = get_idealPath(i,j,data,orientations, 0.75)
        else:
            directions, distances_ = get_idealPath(i,j,data,orientations, 0.5)
        distances[j].append(np.mean(distances_))
        deviations_ = []
        count = 0
        for k in range(len(thetas)):
            if thetas[k] < 0:
                thetas[k] = 360 + thetas[k]
            if thetas[k] - 15 > directions[k] or thetas[k] + 15 < directions[k]:
                count += 1
            deviations_.append(abs(thetas[k] - directions[k]))
        deviations[j].append(np.mean(deviations_))
        accuracy[j].append(float(count / len(directions)))
        plt.plot(ts, thetas, label=labels[j], color='black')
        plt.plot(ts, directions, label='intended path', color='red', linestyle='dotted')
        plt.legend() ; plt.xlabel('Time in seconds') ; plt.ylabel("Orientation (degrees)")
        plt.title("Orientations: {}, Trial {}".format(labels[j], nums[i]))
        plt.show()
    os.chdir('..')

# Summary statistics
# Average Deviation
for key in deviations.keys():
    print("{} deviation is {}".format(str(key), str(np.median(deviations[key]))))
# Percent Accuracy (within 15 degrees)
for key in accuracy.keys():
    print("{} accuracy is {}".format(str(key), str(np.mean(accuracy[key]))))
# Average distance deviation from path
for key in distances.keys():
    print("{} distance is {}".format(str(key), str(np.mean(distances[key]))))
