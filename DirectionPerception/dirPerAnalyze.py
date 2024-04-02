import numpy as np
import re
import constants as c
import statistics as stats
from matplotlib import pyplot as plt

def dirPerceptionAnalyze(subID):
    #Analyzes the data for subject number subID for all three belts and plots the results
    data = parseData(subID)

    #Initialize 2D array w 5 subarrays. First 3 correspond to the different belts. Last 2 correspond to the vibration schemes
    #Each subarray will store the average error (initialized to -1) for that bin for each of the 5 different categories
    angleErrors_bins = []
    angleErrors = [[] for x in range(5)]
    angles = [] #Just for debugging
    for i in range(5):
        angleErrors_bins.append([[] for x in range(constants.NUM_BINS)])
        angles.append([[] for x in range(constants.NUM_BINS)])

    #Counters for the number of different trials. Used to make sure the data is correctly distributed
    numGauss = 0; numSing = 0; numOther = 0; num8mtr = 0; num12mtr = 0; num16mtr = 0;

    # Iterate through belts
    for i in range(len(data)):

        #Iterate through data for each belt
        for j in range(len(data[i][0])):
            subjectAngle = data[i][0][j]
            actualAngle = data[i][1][2 * j]
            vibScheme = data[i][1][(2*j)+1] #0 - single motor, 1 - Gaussian
            angleError = abs(actualAngle - subjectAngle) #REMOVE 'ROUND' HERE!!!!!!!!!!!!

            #Make the sure the error wraps around
            if angleError > 180:
                angleError = 360 - angleError

            #Add the error to the correct bin for the correct belt and the correct vibration scheme
            binNum = int(round(actualAngle/(360/constants.NUM_BINS))) % constants.NUM_BINS
            angleErrors_bins[i][binNum].append(angleError)
            angleErrors[i].append(angleError)
            angles[i][binNum].append(actualAngle)

            if vibScheme == 0:
                angleErrors_bins[3][binNum].append(angleError) #Add error to single-motor array
                angleErrors[3].append(angleError)
                numSing += 1
            elif vibScheme == 1:
                angleErrors_bins[4][binNum].append(angleError) #Add error to Gaussian array
                angleErrors[4].append(angleError)
                numGauss += 1
            else:
                numOther += 1

            if i == 0: num8mtr += 1
            elif i == 1: num12mtr += 1
            elif i == 2: num16mtr += 1


    #Iterate through errors and find the average error for each bin
    for i in range(len(angleErrors_bins)):

        #Do binned results first
        for j in range(len(angleErrors_bins[i])):
            mean_bin = round(stats.mean(angleErrors_bins[i][j]),1)
            #stdev_bin = 0
            stdev_bin = round(stats.stdev(angleErrors_bins[i][j]),1)
            angleErrors_bins[i][j] = [mean_bin, stdev_bin]


        #Do general results
        mean = round(stats.mean(angleErrors[i]),1)
        #stdev = 0
        stdev = round(stats.stdev(angleErrors[i]),1)
        angleErrors[i] = [mean, stdev]



    #Make sure data distribution is correct
    assert numGauss == 108, 'Incorrect number of Gaussian trials'
    assert numSing == 108, 'Incorrect number of single-motor trials'
    assert numOther == 0, 'Some trials are listed as neither Gaussian nor single-motor'
    assert num8mtr == 72, 'Incorrect number of 8-motor trials'
    assert num12mtr == 72, 'Incorrect number of 12-motor trials'
    assert num16mtr == 72, 'Incorrect number of 16-motor trials'

    #Plot results
    degreeAxis = np.linspace(0, 360, constants.NUM_BINS, False)
    titles = ["Average Direction Error: 8-motor Belt","Average Direction Error: 12-motor Belt","Average Direction Error: 16-motor Belt",\
              "Average Direction Error: Single-Motor Vibrations","Average Direction Error: Gaussian Vibrations"]
    for i in range(len(angleErrors_bins)):
        plotErrors(angleErrors_bins[i], degreeAxis, titles[i])



def parseData(subID):
    # Open the files and process them into arrays
    file_8mtr = open("DirPer_8mtr_sub" + str(subID) + ".txt", 'r')
    file_12mtr = open("DirPer_12mtr_sub" + str(subID) + ".txt", 'r')
    file_16mtr = open("DirPer_16mtr_sub" + str(subID) + ".txt", 'r')

    # Store all lines from each file in a single 2D array, element 0 is 8mtr, 1 is 12mtr, and 2 is 16mtr
    lines = [file_8mtr.readlines(), file_12mtr.readlines(), file_16mtr.readlines()]
    for i in range(len(lines)):

        # Parse first line (subject angle response)
        lines[i][0] = lines[i][0].split(',')
        lastNum = lines[i][0][-1]
        lines[i][0][-1] = lastNum[0:len(lastNum) - 1]  # Cut off last two characters due to the \n

        # Parse second line (actual vibration angle and vibration scheme)
        reducedStr = ''
        for iChar in range(len(lines[i][1])):
            char = lines[i][1][iChar]
            prevChar = lines[i][1][max(0, iChar - 1)]

            if char != '\n' and char != '(' and char != ')':
                if char == ',' and prevChar == ')':
                    reducedStr += ' '
                elif char != ',':
                    reducedStr += char

        lines[i][1] = reducedStr.split(' ')


        #Turn string values into numbers
        for j in range(2):
            for k in range(len(lines[i][j])):
                lines[i][j][k] = float(lines[i][j][k])

    return lines


def plotErrors(angleErrors, degreeAxis, title):
    #Plots the error for each bin using a polar plot

    #Make sure array sizes match
    assert len(angleErrors) == len(degreeAxis), "Array sizes do not match"

    #Define two axes based on input arrays
    rads = [error[0] for error in angleErrors] + [angleErrors[0][0]]
    thetas = [(angle/180)*np.pi for angle in degreeAxis] + [0]

    #Plot data
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='polar')
    ax.set_xticks(thetas)
    #ax.set_xticklabels([int(degree) for degree in degreeAxis],fontsize=10)
    ax.set_xticklabels([int(degree) for degree in degreeAxis] + [degreeAxis[0]], fontsize=10)
    ax.set_yticks(np.linspace(0,25,6, False))
    ax.set_yticklabels([0,5,10,15,20,25])
    ax.set_ylim([0, 25])
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location('N')
    ax.set_rlabel_position(90)

    print("Max: " + str(max(angleErrors)[0]))
    # Plots the data
    ax.scatter(thetas, rads, s=15)
    ax.plot(thetas,rads)
    plt.title(title, y=1.08, fontsize=15)
    plt.show()


if __name__ == "__main__":
    constants = c.constants()
    subID = 2
    dirPerceptionAnalyze(subID)