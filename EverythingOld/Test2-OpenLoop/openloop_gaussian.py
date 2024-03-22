

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
import vizcam

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
numMotors = 12

# Defines the motors to fire for each of the cardinal directions
# 0: N | 1: NE | 2: E | 3: SE | 4: S | 5: SW | 6: W | 7: NW | 8: STOP
motors = {} ; motors[8] = {} ; motors[12] = {}
motors[8][0] = [8] ; motors[8][1] = [1]
motors[8][2] = [2] ; motors[8][3] = [3]
motors[8][4] = [4] ; motors[8][5] = [5]
motors[8][6] = [6] ; motors[8][7] = [7]
motors[8][8] = [1,2,3,4,5,6,7,8]
motors[12][0] = [2,1,12] ; motors[12][1] = [12,11]
motors[12][2] = [11,10,9] ; motors[12][3] = [9,8]
motors[12][4] = [8,7,6] ; motors[12][5] = [6,5]
motors[12][6] = [5,4,3] ; motors[12][7] = [3,2]
motors[12][8] = [2,3,4,5,6,7,8,9,10,11,12,1]

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

######################################################################################################
# Control Options

ODYSSEY = 'Odyssey'
MONITOR = 'PC Monitor'

controlOptions = [MONITOR, ODYSSEY]
controlType = controlOptions[viz.choose('How would you like to explore? ', controlOptions)]
if controlType == MONITOR:
	# Use keyboard controls
	headTrack = viztracker.Keyboard6DOF()
	view = viz.MainView
	link = viz.link(headTrack, view)
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
recordPos = numpy.array([]) ; recordOrient = numpy.array([]) ; finished = 1

motionModel = 'go_north'
motionModel = 'go_to_pole'

polePosition1 = [10, 0, 0]
polePosition2 = [0, 0, 10] # x,y,z where y is vertical axis
polePosition3 = [-10, 0, 0]
polePosition4 = [0, 0, -10]

waypoints = {}
waypoints[0] = [0.0, 0.0, 0.0]
waypoints[1] = [6.0, 0.0, 4.0] ; waypoints[2] = [2.0, 0.0, 9.0]
waypoints[3] = [-5.0, 0.0, 9.0] ; waypoints[4] = [-4.0, 0.0, 3.0]
waypoints[5] = [-7.0, 0.0, -6.0] ; waypoints[6] = [4.0, 0.0, -4.0]
waypoints[7] = [0.0, 0.0, 0.0] ; waypoints[8] = [0.0, 0.0, 0.0]

if motionModel=='go_to_pole':
	# These poles are used to provide some sort of orientation
	pole1= vizshape.addCylinder(height = 1.9, radius = 0.1, yAlign=vizshape.ALIGN_MIN)
	pole2 = vizshape.addCylinder(height = 1.9, radius = 0.1, yAlign=vizshape.ALIGN_MIN)
	pole3 = vizshape.addCylinder(height = 1.9, radius = 0.1, yAlign=vizshape.ALIGN_MIN)
	pole4 = vizshape.addCylinder(height = 1.9, radius = 0.1, yAlign=vizshape.ALIGN_MIN)
	pole1.color(viz.BLACK) ; pole2.color(viz.GREEN) ; pole3.color(viz.YELLOW)
	pole4.color(viz.WHITE)

	pole1.setPosition(polePosition1)
	pole2.setPosition(polePosition2)
	pole3.setPosition(polePosition3)
	pole4.setPosition(polePosition4)

	# Commented out so not visible to subject
	############################################################################
	# box1 = vizshape.addBox(size=(4, 5, 4)) ; box1.color(viz.GRAY)
	# box2 = vizshape.addBox(size=(6, 5, 1)) ; box2.color(viz.RED)
	# box3 = vizshape.addBox(size=(2, 5, 5.5)) ; box3.color(viz.GREEN)
	# box4 = vizshape.addBox(size=(4, 5, 3)) ; box4.color(viz.BLACK)
	# box5 = vizshape.addBox(size=(2, 5, 1)) ; box5.color(viz.YELLOW)
	#
	# box1.setPosition([2 ,0, 5])
	# box2.setPosition([-1, 0, 7.5])
	# box3.setPosition([-6, 0, 4.25])
	# box4.setPosition([-2, 0, 2.5])
	# box5.setPosition([-3, 0, -0.5])
	############################################################################

def masterLoop(num):
	global time, polePosition1, polePosition2, motionModel, ser, start, pystart, record, recordPos, recordOrient, finished
	curPos = viz.get(viz.HEAD_POS) # x,y,z position
	curRot = viz.get(viz.HEAD_ORI) # yaw, pitch, roll (or maybe yaw, roll, pitch)
	timeElapsed = viz.getFrameElapsed()
	time += timeElapsed
#	audioControls.audioFinishedCheck()
#	emergencyWallsNormal.popWalls(curPos)

	if motionModel=='go_north':
		desiredAngle = 0
	if motionModel=='go_to_pole':
		dx = waypoints[finished][0] - curPos[0]
		dz = waypoints[finished][2] - curPos[2]
		desiredAngle = math.atan2(dx,dz)*180.0/math.pi

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
	# index = numpy.argmax([numpy.dot(desiredVector, x) for x in directionVectors])
	motorDotProducts = numpy.array([numpy.dot(desiredVector, x) for x in directionVectors])
	indices = motorDotProducts.argsort()[-3:][::-1]

	motorDotProducts = numpy.take(motorDotProducts, indices)
	motorDotProducts = motorDotProducts / numpy.sum(motorDotProducts)

	weights = [] ; motorsToSend = []
	for i in indices:
		motorsToSend.append(motors[numMotors][i][0])
	for weight in motorDotProducts:
		weights.append(2 * int(numpy.interp(weight, [numpy.min(motorDotProducts), numpy.max(motorDotProducts)], [3, 5])))

	distToDest = numpy.sqrt((curPos[0] - waypoints[finished-1][0])**2 + (curPos[2] - waypoints[finished-1][2])**2)

	if distToDest < 0.75 or (finished == 2 and curPos[0] > 6) or (finished == 3 and curPos[0] < 2) or (finished == 3 and curPos[2] > 9) or (finished == 4 and curPos[0] < -4) or (finished == 5 and curPos[2] < 3) or (finished == 6 and curPos[2] < -6) or (finished == 6 and curPos[0] < -7) or (finished == 7 and curPos[0] > 4) or (finished == 8 and curPos[0] < 0):
		print(finished)
		finished += 1
		if finished == 9:
			index = numMotors
			directionsToSend = motors[numMotors][8] ; directionsToSend.insert(0, 255)
			directionsToSend.append(250)
			for num in directionsToSend:
				ser.write(struct.pack('>B', num))
			print(directionsToSend)
			tm.sleep(5.0)
			numpy.save('openloop_positionsG.npy', recordPos)
			numpy.save('openloop_orientationsG.npy', recordOrient)
			ser.write(struct.pack('>B', 255))
			sys.exit(0)
		else:
			directionsToSend = [255]
			for i in range(len(motorsToSend)):
				if weights[i] == 10:
					directionsToSend.append(motorsToSend[i])
			directionsToSend.append(254)
			for i in range(len(motorsToSend)):
				if weights[i] == 8:
					directionsToSend.append(motorsToSend[i])
			directionsToSend.append(253)
			for i in range(len(motorsToSend)):
				if weights[i] == 6:
					directionsToSend.append(motorsToSend[i])
			directionsToSend.append(250)
			print(directionsToSend) ; print(weights)
			for num in directionsToSend:
				ser.write(struct.pack('>B', num))
			tm.sleep(3.0)
			ser.write(struct.pack('>B', 255))
			start = tm.time()


	# Records positional and orientational data every 1 second
	if tm.time() - record > 0.5:
		recordPos = numpy.append(recordPos, curPos) ; recordOrient = numpy.append(recordOrient, curRot)
		record = tm.time()

	if tm.time() - pystart > 10:
		ser.reset_input_buffer()
		ser.reset_output_buffer()
		pystart = tm.time()

viz.callback(viz.TIMER_EVENT,masterLoop)

#This starts the timer.  First value (0) is a timer identifier, second (1/90) is the refresh rate, third (viz.FOREVER) is how long it lasts

viz.starttimer(0,1/90,viz.FOREVER)
