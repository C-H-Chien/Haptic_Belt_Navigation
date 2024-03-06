######################################################################################################

# Imports

import math
import numpy
import random
import sys
import time as tm
import viz
import vizconnect
import vizact
import viztracker
import vizshape

from os.path import exists

#import audioControls
#import emergencyWallsNormal

import lights
import oculus
import steamvr
import winsound
import oculus
import vizfx.postprocess

import serial
import struct

#from random import random # for the random berry spawn location

ser = serial.Serial('COM3')
ser.baudrate= 115200

# Defines the number of motors in the current run
numMotors = 8

# There are 4 possible levels of strength and 3 possible belt sizes
strengths = [1,2,3,4] ; beltSizes = [8,12]

# This is the main dictionary on what data to send
directionsToSend = {}

for size in beltSizes:
	directionsToSend[size] = {}
	for strength in strengths:
		directionsToSend[size][strength] = {}

# Defines the motors to fire for each of the cardinal directions
# 0: N | 1: NE | 2: E | 3: SE | 4: S | 5: SW | 6: W | 7: NW | 8: STOP
motors = {} ; motors[8] = {} ; motors[12] = {}
motors[8][0] = [8] ; motors[8][1] = [1]
motors[8][2] = [2] ; motors[8][3] = [3]
motors[8][4] = [4] ; motors[8][5] = [5]
motors[8][6] = [6] ; motors[8][7] = [7]
motors[8][8] = [1,2,3,4,5,6,7,8]
motors[12][0] = [2,13,12] ; motors[12][1] = [12,11]
motors[12][2] = [11,10,9] ; motors[12][3] = [9,8]
motors[12][4] = [8,7,6] ; motors[12][5] = [6,5]
motors[12][6] = [5,4,3] ; motors[12][7] = [3,2]
motors[12][8] = [2,3,4,5,6,7,8,9,10,11,12,13]

# Defines unit vectors for each direction
# 0: N | 1: NE | 2: E | 3: SE | 4: S | 5: SW | 6: W | 7: NW | 8: STOP
directionVectors = []
directionVectors.append([0,1])
directionVectors.append([1,1] / numpy.sqrt(2))
directionVectors.append([1,0])
directionVectors.append([1,-1] / numpy.sqrt(2))
directionVectors.append([0,-1])
directionVectors.append([-1,-1] / numpy.sqrt(2))
directionVectors.append([-1,0])
directionVectors.append([-1,1] / numpy.sqrt(2))
directionVectors.append([0,0])

# Defines each direction in text
directions = []
directions.append('north') ; directions.append('north east')
directions.append('east') ; directions.append('south east')
directions.append('south') ; directions.append('south west')
directions.append('west') ; directions.append('north west')
directions.append('stop')

# Populates the directionsToSend dictionary
for size in beltSizes:
	for strength in strengths:
		for i in range(len(directions)):
			if i == 8:
				directionsToSend[size][strength][i] = motors[size][i] + [0,200,0]
			elif strength == 1:
				directionsToSend[size][strength][i] = motors[size][i] + [0,15,0]
			elif strength == 2:
				directionsToSend[size][strength][i] = motors[size][i] + [0,25,0]
			elif strength == 3:
				directionsToSend[size][strength][i] = motors[size][i] + [0,38,0]
			elif strength == 4:
				directionsToSend[size][strength][i] = motors[size][i] + [0,50,0]

######################################################################################################
# Control Options

ODYSSEY = 'Odyssey'
MONITOR = 'PC Monitor'

controlOptions = [MONITOR, ODYSSEY]
controlType = controlOptions[viz.choose('How would you like to explore? ', controlOptions)]
if controlType == MONITOR:
	# Use keyboard controls
	headTrack = viztracker.Keyboard6DOF()
	link = viz.link(headTrack, viz.MainView)
	headTrack.eyeheight(1.6)
	link.setEnabled(True)
	viz.go()
	viz.setOption('viz.fullscreen.x','0')
	viz.setOption('viz.fullscreen.y','0')
	viz.setOption('viz.fullscreen.width','1024')
	viz.setOption('viz.fullscreen.height','1024')
	hmdName = 'PC'

elif controlType == ODYSSEY:
	# code taken from Greg's Occlusion Study
	# add Odyssey tracker
	ODTracker = steamvr.HMD().getSensor()

	# link the ISTracker to the camera
	link = viz.link(ODTracker, viz.MainView)
	viz.window.setFullscreenMonitor(2)

	viz.window.setSize([1200,750])

viz.go()

##################################################################################################
# Initialize environment

viz.clearcolor(0,0.4,1.0) # blue sky

viz.add('Models/ground4.3DS') # ground plane

text_score = viz.addText('BLANK',parent=viz.SCREEN) # display info on the screen
text_score.setPosition(0,0.9)

# points in the desired direction for subject
compassNeedle = vizshape.addBox(size=(0.5,0.1,10),color = viz.RED,zAlign=vizshape.ALIGN_MIN,xAlign=vizshape.ALIGN_CENTER)
compassNeedle.setEuler(0,0,0)

######################################################################################################
# Experiment Loop
# Experiment variables
time = 0
timeStamp = 0
start = tm.time()
pystart = tm.time()
record = tm.time()
recordPos = numpy.array([]) ; recordOrient = numpy.array([]) ; finished = 0

motionModel = 'go_north'
motionModel = 'go_to_pole'

polePosition1 = [0, 0, 9.5]
polePosition2 = [5, 0, 5.0] # x,y,z where y is vertical axis

if motionModel=='go_to_pole':
	pole1= vizshape.addCylinder(height = 1.9, radius = 0.1, yAlign=vizshape.ALIGN_MIN)
	pole2 = vizshape.addCylinder(height = 1.9, radius = 0.1, yAlign=vizshape.ALIGN_MIN)
	pole1.color(viz.BLACK) ; pole2.color(viz.GREEN)

	pole1.setPosition(polePosition1)
	pole2.setPosition(polePosition2)

	box1 = vizshape.addBox(size=(3, 5, 4)) ; box1.color(viz.GRAY)
	box2 = vizshape.addBox(size=(3, 5, 10)) ; box2.color(viz.GRAY)
	box3 = vizshape.addBox(size=(10, 5, 3)) ; box3.color(viz.YELLOW)
	box4 = vizshape.addBox(size=(4, 5, 3)) ; box4.color(viz.YELLOW)
	box5 = vizshape.addBox(size=(3, 5, 9)) ; box5.color(viz.RED)

	box1.setPosition([3 ,0, 2])
	box2.setPosition([-3, 0, 5])
	box3.setPosition([2, 0, 11.5])
	box4.setPosition([3.5, 0, 7.5])
	box5.setPosition([7, 0, 12.5])

def masterLoop(num):
	global time, polePosition1, polePosition2, directionsToSend, motionModel, ser, start, pystart, record, recordPos, recordOrient, finished
	curPos = viz.get(viz.HEAD_POS) # x,y,z position
	curRot = viz.get(viz.HEAD_ORI) # yaw, pitch, roll (or maybe yaw, roll, pitch)
	timeElapsed = viz.getFrameElapsed()
	time += timeElapsed
#	audioControls.audioFinishedCheck()
#	emergencyWallsNormal.popWalls(curPos)

	if motionModel=='go_north':
		desiredAngle = 0
	if motionModel=='go_to_pole':
		if finished == 0:
			dx = polePosition1[0] - curPos[0]
			dz = polePosition1[2] - curPos[2]
			desiredAngle = math.atan2(dx,dz)*180.0/math.pi
		else:
			dx = polePosition2[0] - curPos[0]
			dz = polePosition2[2] - curPos[2]
			desiredAngle = math.atan2(dx, dz)*180.0/math.pi

	compassNeedle.setPosition(curPos[0],0,curPos[2])
	compassNeedle.setEuler(desiredAngle,0,0)
	screenMessage = " Current Angle: %d\n Desired: %d" % (curRot[0],desiredAngle)
	text_score.message(screenMessage)

	angleError = curRot[0]-desiredAngle

	if angleError > 180:
		angleError -= 360
	elif angleError < -180:
		angleError += 360

	desiredVector = [-numpy.sin((numpy.pi / 180) * angleError), numpy.cos((numpy.pi / 180) * angleError)]
	index = numpy.argmax([numpy.dot(desiredVector, x) for x in directionVectors])

	if finished == 0:
		distToDest = numpy.sqrt((curPos[0] - polePosition1[0])**2 + (curPos[2] - polePosition1[2])**2)
	else:
		distToDest = numpy.sqrt((curPos[0] - polePosition2[0])**2 + (curPos[2] - polePosition2[2])**2)

	if distToDest < 0.5 and finished == 0:
		index = numMotors ; finished = 1
	elif distToDest < 0.5 and finished == 1:
		index = numMotors; finished = 2
		numpy.save('positions_1B.npy', recordPos)
		numpy.save('orientations_1B.npy', recordOrient)
	elif distToDest < 0.5 and finished == 2:
		index = numMotors

	print(directionsToSend[numMotors][4][index])
	if index == numMotors:
		for num in directionsToSend[numMotors][4][index]:
			ser.write(struct.pack('>B', num))
		start = tm.time()
	elif tm.time() - start > 0.05:
		for num in directionsToSend[numMotors][4][index]:
			ser.write(struct.pack('>B',num))
		start = tm.time()
	if tm.time() - record > 1 and finished < 2:
		recordPos = numpy.append(recordPos, curPos) ; recordOrient = numpy.append(recordOrient, curRot)
		record = tm.time()
	if tm.time() - pystart > 10:
		ser.reset_input_buffer()
		ser.reset_output_buffer()
		pystart = tm.time()


viz.callback(viz.TIMER_EVENT,masterLoop)

#This starts the timer.  First value (0) is a timer identifier, second (1/90) is the refresh rate, third (viz.FOREVER) is how long it lasts

viz.starttimer(0,1/90,viz.FOREVER)
