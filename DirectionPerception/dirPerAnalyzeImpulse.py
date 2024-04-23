import numpy as np
import re
import constants as c
import statistics as stats
from matplotlib import pyplot as plt
from itertools import cycle

def dirPerceptionAnalyze(subID):
    #Analyzes the data for subject number subID for all three belts and plots the results
    data = parseData(subID)
    #Initialize 2D array w 5 subarrays. First 3 correspond to the different belts. Last 2 correspond to the vibration schemes
    #Each subarray will store the average error (initialized to -1) for that bin for each of the 5 different categories
    angleErrors_bins = []
    actualErrors_bins = []
    angleErrors_time = []
    angleErrors = [[] for x in range(1)]
    angles = [] #Just for debugging

    for i in range(1):
        angleErrors_bins.append([[] for x in range(constants.NUM_BINS)])
        angleErrors_time.append([[] for x in range(constants.NUM_BINS)])
        actualErrors_bins.append([[] for x in range(constants.NUM_BINS)])
        angles.append([[] for x in range(constants.NUM_BINS)])

    #Counters for the number of different trials. Used to make sure the data is correctly distributed
    numGauss = 0; numSing = 0; numOther = 0; num8mtr = 0; num12mtr = 0; num16mtr = 0;

    # Iterate through belts
    for i in range(len(data)):
        #Iterate through data for each belt
        for j in range(len(data[i][0])):
            subjectAngle = data[i][0][j]
            responseTime = data[i][2][j] - data[i][2][0]
            actualAngle = data[i][1][2 * j]
            angleError = abs(actualAngle - subjectAngle) #REMOVE 'ROUND' HERE!!!!!!!!!!!!
            #Make the sure the error swraps around
            if angleError > 180:
                angleError = 360 - angleError

            #Add the error to the correct bin for the correct belt and the correct vibration scheme
            binNum = int(actualAngle / 22.5)
            print(binNum)
            
            angleErrors_bins[i][binNum].append(angleError)
            actualErrors_bins[i][binNum].append(angleError)
            angleErrors_time[i][binNum].append(responseTime)
            angleErrors[i].append(angleError)
            angles[i][binNum].append(subjectAngle)
            num16mtr += 1

    #Iterate through errors and find the average error for each bin
    for i in range(len(angleErrors_bins)):
        for j in range(constants.NUM_BINS):
            mean_bin = round(stats.mean(angleErrors_bins[i][j]),1)
            stdev_bin = round(stats.stdev(angleErrors_bins[i][j]),1)
            angleErrors_bins[i][j] = [mean_bin, stdev_bin]


        #Do general results
        mean = round(stats.mean(angleErrors[i]),1)
        #stdev = 0
        stdev = round(stats.stdev(angleErrors[i]),1)
        angleErrors[i] = [mean, stdev]

    assert num16mtr == 160, 'Incorrect number of 16-motor trials'
   
    #Plot results
    degreeAxis = np.linspace(0, 360, constants.NUM_BINS, False)
    titles = ["Average Direction Error: 16-motor Belt"]
    for i in range(len(angleErrors_bins)):
        plotErrors(angleErrors_bins[i], degreeAxis, titles[i], angles[i])
        for m in range(constants.NUM_BINS):
            time = angleErrors_time[i][m]
            errors = actualErrors_bins[i][m]
            plt.plot(time, errors)
            plt.xlabel('Time(seconds)') 
            plt.ylabel('Error(degrees)') 
            plt.title('Adaptation for motor at ' +str(22.5*m) + ' degrees')
            plt.show()
            
        
    



def parseData(subID):
    file_16mtr = open("DirPer_16mtr_sub" + str(subID) + ".txt", 'r')
    lines = [file_16mtr.readlines()]
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

        # Parse third line (response time)
        lines[i][2] = lines[i][2].split(',')
        lastNum = lines[i][2][-1]
        lines[i][2][-1] = lastNum[0:len(lastNum) - 1]  # Cut off last two characters due to the \n


        #Turn string values into numbers
        for j in range(3):
            for k in range(len(lines[i][j])):
                lines[i][j][k] = float(lines[i][j][k])

    return lines


def plotErrors(angleErrors, degreeAxis, title, angles):
    #Plots the error for each bin using a polar plot
    #Make sure array sizes match
    assert len(angleErrors) == len(degreeAxis), "Array sizes do not match"

    #Define two axes based on input arrays
    # Convert degreeAxis to radians and complete the loop for the plot
    thetas = [(angle/180)*np.pi for angle in degreeAxis] + [0]
    rads = [error[0] for error in angleErrors] + [angleErrors[0][0]]

    #Plot data
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='polar')
    ax.set_xticks(thetas)
    #ax.set_xticklabels([int(degree) for degree in degreeAxis],fontsize=10)
    ax.set_xticklabels([int(degree) for degree in degreeAxis] + [degreeAxis[0]], fontsize=10)
    ax.set_yticks(np.linspace(0,35,8, False))
    ax.set_yticklabels([0,5,10,15,20,25,30,35])
    ax.set_ylim([0, 35])
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location('N')
    ax.set_rlabel_position(90)
    # Plots the data
    ax.scatter(thetas, rads, s=15)
    ax.plot(thetas,rads)
    # Markers cycle for different sublists in angles
    markers = cycle(['o', 's', 'D', '^', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x'])
    # Plot each sublist in angles
    degree = 0
    for sublist in angles:
        angle_rads = [(angle/180)*np.pi for angle in sublist]
        print(sublist)
        marker = next(markers)
        label = 'motor at ' + str(degree) + ' degree'
        ax.scatter(angle_rads, [max(rads) * 0.9] * len(sublist), s=30, alpha=0.75, marker=marker, label=label)
        degree += 22.5
    plt.legend()
    plt.title(title, y=1.08, fontsize=15)
    plt.show()
    print("Max: " + str(max(angleErrors)[0]))
    


if __name__ == "__main__":
    constants = c.constants()
    subID = 3
    dirPerceptionAnalyze(subID)