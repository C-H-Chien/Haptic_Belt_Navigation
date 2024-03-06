
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

ser = serial.Serial('COM3')
ser.baudrate= 115200

# Defines the number of motors in the current run
numMotors = 12
# There are 4 possible levels of strength and 3 possible belt sizes
#strengths = [1,2,3,4] ; beltSizes = [8,12]
# This is the main dictionary on what data to send
#directionsToSend = {}
#for size in beltSizes:
#	directionsToSend[size] = {}
#	for strength in strengths:
#		directionsToSend[size][strength] = {}

# Defines the motors to fire for each of the cardinal directions
# 0: N | 1: NE | 2: E | 3: SE | 4: S | 5: SW | 6: W | 7: NW | 8: STOP
#motors = {} ; motors[8] = {} ; motors[12] = {}
#motors[8][0] = [8] ; 
#motors[8][1] = [1]
#motors[8][2] = [2] ; 
#motors[8][3] = [3]
#motors[8][4] = [4] ; 
#motors[8][5] = [5]
#motors[8][6] = [6] ; 
#motors[8][7] = [7]
#motors[8][8] = [1,2,3,4,5,6,7,8]
#motors[12][0] = [13] ; 
#motors[12][1] = [12]
#motors[12][2] = [11] ; 
#motors[12][3] = [10]
#motors[12][4] = [9] ; 
#motors[12][5] = [8]
#motors[12][6] = [7] ; 
#motors[12][7] = [6]
#motors[12][8] = [5] ; 
#motors[12][9] = [4]
#motors[12][10] = [3] ; 
#motors[12][11] = [2]
#motors[12][12] = [2,3,4,5,6,7,8,9,10,11,12,13]


if numMotors==12:
	motorIDs = [13,12,11,10,9,8,7,6,5,4,3,2]
	motorAngles = [30,60,90,120,150,180,-150,-120,-90,-60,-30,0] # 0 straight ahead, positive to the left..
if numMotors==8:
	motorIDs = [12,11,10,9,8,7,6,5]
	motorAngles = [45,90,135,180,-135,-90,-45,0]

# Defines unit vectors for each direction
# 0: N | 1: NE | 2: E | 3: SE | 4: S | 5: SW | 6: W | 7: NW | 8: STOP
#directionVectors = []
#for i in range(numMotors):
#	angle = (2*numpy.pi*i) / numMotors
#	angle_adj = -angle + (numpy.pi / 2)
#	directionVectors.append([numpy.cos(angle_adj), numpy.sin(angle_adj)])
#directionVectors.append([0,0])


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

# Lets us display current and desired angle on screen for debugging
text_score = viz.addText('BLANK',parent=viz.SCREEN) # display info on the screen
text_score.setPosition(0,0.9)

# points in the desired direction for subject/debugging
compassNeedle = vizshape.addBox(size=(0.5,0.1,10),color = viz.RED,zAlign=vizshape.ALIGN_MIN,xAlign=vizshape.ALIGN_CENTER)
compassNeedle.setEuler(0,0,0)

######################################################################################################
# Experiment Loop

# Experiment variables

time = 0
timeStamp = 0
timeLastMessage = tm.time()
record = tm.time()
start = tm.time()
pystart = tm.time()
recordPos = numpy.array([]) ; recordOrient = numpy.array([]) ; finished = 0

motionModel = 'go_north'
motionModel = 'go_to_pole'

# Defines the two pole positions (position1 is a waypoint, position2 is the goal)
polePosition1 = [0, 0, 13.5]
polePosition2 = [6.5, 0, 12.5] # x,y,z where y is vertical axis

if motionModel=='go_to_pole':
	# Creates the pole and box objects for the VR environment
	pole1= vizshape.addCylinder(height = 1.9, radius = 0.1, yAlign=vizshape.ALIGN_MIN)
	pole1.color(viz.BLACK) ;
	pole1.setPosition(polePosition1)


def masterLoop(num):
	global time, timeLastMessage, polePosition1, motionModel, ser, record, start, pystart, recordPos, recordOrient, finished, motorIDs, motorAngles
	curPos = viz.get(viz.HEAD_POS) # x,y,z position
	curRot = viz.get(viz.HEAD_ORI) # yaw, pitch, roll (or maybe yaw, roll, pitch) in deg
	timeElapsed = viz.getFrameElapsed()
	time += timeElapsed # this doesn't seem to be an accurate measure of time
#	audioControls.audioFinishedCheck()
#	emergencyWallsNormal.popWalls(curPos)

	# Calculate angle to desired position
	dx = polePosition1[0] - curPos[0]
	dz = polePosition1[2] - curPos[2]
	desiredAngle = math.atan2(dx,dz)*180.0/math.pi
	angleError = curRot[0]-desiredAngle

	# Adjust the red debugging need that points to the desired direction. Also onscreen debug message
	compassNeedle.setPosition(curPos[0],0,curPos[2])
	compassNeedle.setEuler(desiredAngle,0,0)
	screenMessage = " Current Angle: %d\n Desired: %d\n Error: %d" % (curRot[0],desiredAngle,angleError)
	text_score.message(screenMessage)

	# Some trig adjustments
	angleError = wrapTo180(angleError)
	
	# Compose message using a particular paridigm
	message = gaussBlob(angleError,motorIDs,motorAngles)
	#message = closest_k_motors(angleError,motorIDs,motorAngles,1)
	
	# Send message over Serial at the desired frame rate
	if tm.time()-timeLastMessage>0.1:
		message = [255] + message + [254]
		timeLastMessage = tm.time()
		print(message)
		for num in message:
			ser.write(struct.pack('B',num)) # convert python ints to C Serial bytes for tranmission
		

	# Here, we flush the pyserial cache every 10 seconds to prevent overflow
	if tm.time() - pystart > 10:
		ser.reset_input_buffer()
		ser.reset_output_buffer()
		pystart = tm.time()

def closest_k_motors(angleError,motorIDs,motorAngles,k):
	angDiff = []
	closestID = []
	power = []
	for ang in motorAngles:
		x = angleError
		y = ang
		diff = min(360 - abs(x - y), abs(x - y))
		angDiff.append(diff)
	sortable = numpy.array(angDiff)
	minIndices = sortable.argsort()[:k]
	for i in range(len(motorAngles)):
		motorOn = False
		for im in minIndices:
			if i==im:
				motorOn = True
		if motorOn:
			power.append(250)
		else:
			power.append(0)
	return power
	
def gaussBlob(angleError,motorIDs,motorAngles):
	motorGauss = []
	for ang in motorAngles:
		pdf = vonMises(ang,angleError)
		motorGauss.append(int(250*pdf))
	return motorGauss

def vonMises(x,mu):
#	kappa = 10
#	I0_kappa = 2815.7 # calculate this in matlab b/c scipy doesnt work in python 2.7..
#	kappaNorm = 1.2450
	kappa = 5
	I0_kappa = 27.2399
	kappaNorm = 0.8671
#	kappa = 2
#	I0_kappa = 2.2796
#	kappaNorm = 0.5159
	normalizer = 1 / (2*numpy.pi*I0_kappa) * 1/kappaNorm # last term makes it so max value of pdf is 1 when x=mu. (no longer integrates to 1)
	term = numpy.exp(kappa*numpy.cos((x-mu)*numpy.pi/180))
	pdf = normalizer * term
	return pdf

def wrapTo180(angleError):
	if angleError > 180:
		angleError -= 360
	elif angleError < -180:
		angleError += 360
	return angleError
	
viz.callback(viz.TIMER_EVENT,masterLoop)
#This starts the timer.  First value (0) is a timer identifier, second (1/90) is the refresh rate, third (viz.FOREVER) is how long it lasts
viz.starttimer(0,1/90.01,viz.FOREVER)
