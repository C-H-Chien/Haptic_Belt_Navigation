###################################################################################################################
# Imports
import os
import math
import numpy as np
import random
import sys
import time as tm
import viz
import vizconnect
import vizact
import viztracker
import vizshape
import lights #file
import oculus
import steamvr
import winsound
import oculus
import vizfx.postprocess
import serial
import struct

import constants as c 


###################################################################################################################
#Main function which calls all others

def runLocomotionSimulation(_port, _numMotors, _showHelpers, _subID, _warmup):
	'''
	Main fucntion that initiates simulation
	'''
	global numMotors, ser, showHelpers, constants, subID, warmup, waypoints
	
	#Initialize constants class to access other variables 
	constants = c.constants()
	
	#Assign input variables to global counterparts
#	ser = serial.Serial(_port)
#	ser.baudrate= constants.SERIAL_BAUDRATE
	numMotors = _numMotors
	subID = _subID
	warmup = _warmup
	showHelpers = _showHelpers 
	
	#Setup controls, environment, and variable order for the test
	setupControls()
	initializeEnvironment()
	arrangeVariableOrder()
	waypoints = setNextPath()

	#Initiate main loop
	viz.callback(viz.TIMER_EVENT, masterLoop)
	#This starts the timer.  First value (0) is a timer identifier, second (1/90) is the refresh rate, third (viz.FOREVER) is how long it lasts
	viz.starttimer(0,constants.REFRESH_RATE,viz.FOREVER)
	


	
############################################################################################################
#Biggest function which handles most of the processing 

def masterLoop(num):
	'''
	The main function that handles the belt functionality and communicates with the belt hardware
	'''
	global pathTime, ser, timer, waypoints, waypointCounter, hitWaypoint, sendStopSignal, reorient, constants, waypointPole
		
	#Determine current location of user
	curPos = viz.get(viz.HEAD_POS) # x,y,z position
	curRot = viz.get(viz.HEAD_ORI) # yaw, pitch, roll 
	timeElapsed = viz.getFrameElapsed()
	pathTime += timeElapsed
	
	#Check if the current state is reorientation
	if reorient:
		reorientate(curPos, curRot) #wait until subject is in correct location facing correct direction
	
	
	#If not reorienting, send cues to the belt based on subject's location relative to the next waypoint in their current path
	if not reorient:
		#Calculate distance to the current waypoint
		dx = waypoints[waypointCounter][0] - curPos[0]
		dz = waypoints[waypointCounter][2] - curPos[2]
		distToDest = np.sqrt(dx**2 + dz**2)
		
		# move pole to waypoint 
		if showHelpers:
			waypointPole.visible(viz.ON)
			waypointPole.setPosition(waypoints[waypointCounter][0],waypoints[waypointCounter][1],waypoints[waypointCounter][2])
		
		#If user is close enough to current waypoint, make next waypoint the target 
		if distToDest < constants.WAYPOINT_RADIUS:
			hitWaypoint = True 
			sendStopSignal = True
			waypointCounter += 1
				
			#Find error in orientation with respect to new waypoint 
			if waypointCounter < len(waypoints):
				dx = waypoints[waypointCounter][0] - curPos[0]
				dz = waypoints[waypointCounter][2] - curPos[2]
			
		#Find error in orientation
		desiredAngle = math.atan2(dx, dz)*180.0/math.pi
		angleError = curRot[0]- desiredAngle
		OGangleError = angleError #save unadjusted angle error for later (used in single_motor vibration mode) 
		
		#Adjust angle for simplicity 
		angleError = wrapTo180(angleError)
		
		#Update the on-screen compass and label
		compassNeedle.setPosition(curPos[0],0,curPos[2])
		compassNeedle.setEuler(desiredAngle,0,0)
		screenMessage = " Current Angle: %d\n Desired: %d" % (curRot[0],desiredAngle)
		text_score.message(screenMessage)

		#Determine motor intensities depending on the vibration type
		if vibrationType == 'gaussian':
			#Find Gaussian distribution for the motors
			motorIntensities = circularGaussian(numMotors, constants.GAUSSIAN_SD, -angleError)
			#Round intensities to whole number (0-255) and set all values below 20% intensity to 0
			motorIntensities = [int(round(intensity)) if intensity >= constants.GAUSSIAN_CUTOFF*255 else 0 for intensity in motorIntensities]
			
		elif vibrationType == 'single':
			motorIntensities = numMotors*[0]
			#Determine closest motor and set its intensity to 100%
			motorToActivate = int(round(-OGangleError/(360/numMotors)))% numMotors #%numMotors prevents edge cases where this rounds to numMotors
			motorIntensities[motorToActivate] = 255	
		
		
		#Determine which signal (belt off, stop, or current motor intensities) needs to be sent to the belt
		dataToSend = chooseSignal(motorIntensities)
		
		#Write signal to the belt periodically 
		if tm.time() - timer >= constants.WRITE_PERIOD:
			
			#Reset timer 
			timer = tm.time()
			
			#Write to motors 
#			for num in dataToSend:
#				ser.write(struct.pack('>B', num))
			print(dataToSend)
		
		
		#Update buffers and subject tracking
		checkTimers(curPos,curRot)
		
		#Reset for next trial if last waypoint in the path is reached (or end simulation if this was the last path)
		if waypointCounter == len(waypoints):
			resetTrial()

	
		
		
######################################################################################################################
#Helper functions - in the order they appear in the code 

def setupControls():
	'''
	Sets up the control method 
	'''
	ODYSSEY = 'Odyssey'
	MONITOR = 'PC Monitor'

	controlOptions = [MONITOR, ODYSSEY]
	controlType = controlOptions[viz.choose('How would you like to explore? ', controlOptions)]

	if controlType == MONITOR:
		# Use keyboard controls
		headTrack = viztracker.Keyboard6DOF()
		view = viz.MainView
		view.collision(viz.ON)
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

	
	
def initializeEnvironment():
	'''
	Prepares the vizard environment
	'''
	global compassNeedle, text_score, pathTime, timer, onTimer, stopTimer, bufferTimer, recordTimer, recordPos, recordOrient, \
		waypointCounter, hitWaypoint, sendStopSignal, stopSignal, beltOffSignal, degreeAxis, pathCounter, poleToGoTo, \
		poleToFace, reorient, atPoleToGoTo, facingPoleToFace, reorientStarted, waypoints, onTime, totalPaths, waypointPole 
	
	viz.clearcolor(0,0.4,1.0) #blue sky
	viz.add('Models/ground4.3DS') #ground plane - need to have these files in directory 
	viz.MainView.collision(viz.OFF) #Don't allow viewpoint to collide with reorientation poles (seems to be on automatically otherwise)  
		
	#Initialize compass needle and angle display label
	text_score = viz.addText('BLANK',parent=viz.SCREEN) # display info on the screen
	text_score.setPosition(0,0.9)
	compassNeedle = vizshape.addBox(size=(0.5,0.1,10),color = viz.RED,zAlign=vizshape.ALIGN_MIN,xAlign=vizshape.ALIGN_CENTER)
	compassNeedle.setEuler(0,0,0)
	
	#Hide these for now
	compassNeedle.visible(viz.OFF)
	text_score.visible(viz.OFF)
	
	#Define 'stop' and 'beltOff' signals
	stopSignal = [constants.MSG_START] + numMotors*[255] + [constants.MSG_END]
	beltOffSignal = [constants.MSG_START] + numMotors*[0] + [constants.MSG_END]
	
	#Prepare for Gaussian vibration type
	degreeAxis = np.linspace(0,360,numMotors,False)
	degreeAxis = [wrapTo180(degree) for degree in degreeAxis]

	#Set up timers and other variables
	pathTime = 0 #Total runtime
	timer = tm.time() #General timer for motor writing
	onTimer = tm.time() - constants.WRITE_PERIOD #Timer to measure time the motors are on
	stopTimer = 0 #Timer to measure time the stop signal is on 
	bufferTimer = tm.time()
	recordTimer = tm.time()
	reorientTimer = tm.time()
	recordPos = np.array([]); recordOrient = np.array([]); waypointCounter = 0; hitWaypoint = False; sendStopSignal = False;
	pathCounter = 1
	onTime = constants.CONTROL_PERIOD
	
	#Define total number of paths to determine when to exit system
	totalPaths = 4
	if not warmup:
		totalPaths *= constants.REPS_PER_COND
	
	#Insert two poles for subject reorientation before next trial begins 
	poleToGoTo = vizshape.addCylinder(height = constants.POLE_TGT_HEIGHT, radius = constants.POLE_TGT_RADIUS, yAlign=vizshape.ALIGN_MIN)
	poleToFace = vizshape.addCylinder(height = constants.POLE_TF_HEIGHT, radius = constants.POLE_TF_RADIUS, yAlign=vizshape.ALIGN_MIN)
	poleToGoTo.color(viz.YELLOW) ; poleToFace.color(viz.RED); 
	poleToGoTo.setPosition(constants.POLE_TGT_POS); poleToFace.setPosition(constants.POLE_TF_POS) 
	
	# Waypoint pole visualization
	waypointPole = vizshape.addCylinder(height = constants.POLE_TGT_HEIGHT, radius = constants.POLE_TGT_RADIUS, yAlign=vizshape.ALIGN_MIN)
	waypointPole.color(viz.GREEN)
	waypointPole.visible(viz.OFF)
	
	#Set variables to begin trial with reorientation 
	reorient = True
	atPoleToGoTo = False
	facingPoleToFace = False
	reorientStarted = False
	
	


def arrangeVariableOrder():
	'''
	Prepares the order of gaussian/single-motor and continuous/discrete for each run
	'''
	global onTime, variableOrder
	
	#Standard order (only relevant for warmup) is single motor first, and continuous first
	variableOrder = [['single',constants.CONTROL_PERIOD],['single',constants.DISCRETE_ON_TIME], \
						['gaussian',constants.CONTROL_PERIOD],['gaussian',constants.DISCRETE_ON_TIME]] #Multiply by num repetitions for each condition
	
	#If warmup, only do each combination once. Otherwise do reps_per_cond repetitions for each condition 
	if not warmup:
		variableOrder *= int(constants.REPS_PER_COND)
		random.shuffle(variableOrder) #Randomize order


def setNextPath():
	'''
	Set the next path in the list of paths (this is stored in a txt file)
	'''
	global numMotors,subID,pathCounter,warmup, variableOrder, vibrationType, onTime
	
	#Set variables based on randomized order
	currVariables = variableOrder[pathCounter-1]
	vibrationType = currVariables[0]
	onTime = currVariables[1]
	
	#Initialize path as an empty array
	path = []
	
	#Read data from file into array 
	if warmup:
		pathsFile = open('Paths_warmups.txt','r')
	else: 
		pathsFile = open('Paths_sub'+str(subID)+'_'+str(numMotors)+'mtr.txt','r')
		
	lines = pathsFile.readlines()
	pathLine = lines[pathCounter-1].split(',')
	
	for i in range(0,len(pathLine),3):
		waypoint = []
		for j in range(3):
			waypoint.append(float(pathLine[i+j]))
		
		path.append(waypoint)
		
	#Close file after reading is complete
	pathsFile.close()
	
	print('Next path has been set')
	return np.array(path)
	


def reorientate(curPos,curRot):
	'''
	Handles functionality for reseting the subject's position and orientations between trials
	'''
	global atPoleToGoTo, facingPoleToFace, reorientTimer, reorient, pathTime, timer, onTimer, stopTimer, bufferTimer, recordTimer, \
			reorientTimer, recordPos, recordOrient,waypointCounter, hitWaypoint, sendStopSignal, poleToFace, poleToGoTo, showHelpers, \
			compassNeedle, text_score, reorientStarted
		
	#Calculate distance to poleToGoTo
	dx = constants.POLE_TGT_POS[0] - curPos[0]
	dz = constants.POLE_TGT_POS[2] - curPos[2]
	distToPole = np.sqrt(dx**2 + dz**2)
	
	#Check subjects position
	if distToPole < constants.REORIENT_RADIUS:
		#Start the timer when subject reaches pole
		atPoleToGoTo = True
	else:
		atPoleToGoTo = False

	#Check subjects orientation
	if  (-constants.REORIENT_YAW_ERROR < curRot[0] < constants.REORIENT_YAW_ERROR) and (-constants.REORIENT_PITCH_ERROR < curRot[1] < constants.REORIENT_PITCH_ERROR) \
		and (-constants.REORIENT_ROLL_ERROR < curRot[2] < constants.REORIENT_ROLL_ERROR):
		facingPoleToFace = True
	else: 
		facingPoleToFace = False
		
	
	#Complete reorientation or wait until conditions are met
	if atPoleToGoTo and facingPoleToFace:
		if not reorientStarted:
			print('Subject orientation is good, wait for timer...')
			reorientTimer = tm.time()
			reorientStarted = True
		elif tm.time() - reorientTimer >= constants.REORIENT_PERIOD:
			#Exit reorientat mode 
			reorient = False
		
			#Reset timers for next trial
			pathTime = 0 #Total runtime
			timer = tm.time() #General timer for motor writing
			onTimer = tm.time() - constants.WRITE_PERIOD #Timer to measure time the motors are on
			stopTimer = 0 #Timer to measure time the stop signal is on 
			bufferTimer = tm.time()
			recordTimer = tm.time()
			reorientTimer = tm.time()
		
			#Reset variables
			recordPos = np.array([]); recordOrient = np.array([]); waypointCounter = 0; hitWaypoint = False; sendStopSignal = False;
			
			#Hide reorientation poles
			poleToFace.visible(viz.OFF)
			poleToGoTo.visible(viz.OFF)
			
			#Show helpers if relevant
			if showHelpers:
				compassNeedle.visible(viz.ON) #show compass
				text_score.visible(viz.ON) #show orientation info 
			print('Successfully reoriented, new trial starting!')
		
	else:
		print('Subject not oriented correctly...')
		reorientStarted = False
		

def wrapTo180(angleError):
	'''
	Returns input angleError as an angle between -180 and 180
	'''
	if angleError > 180:
		angleError -= 360
	elif angleError < -180:
		angleError += 360
	return angleError
	
	
def circularGaussian(numMotors, gaussianSD, mean):
	'''
	Returns a numpy array with length numMotors consisting of a Guassian with standard deviation 'gaussianSD' and mean of 'mean'
	This isn't a perfect Gaussian since it implements a sum of three Gaussians each separated by 360 degrees to make it 'circular'
	'''
	global degreeAxis
	circularGaussian = 255*np.array([np.exp(-0.5*((x-mean)/gaussianSD)**2)+np.exp(-0.5*((x-mean-360)/gaussianSD)**2)\
						+np.exp(-0.5*((x-mean+360)/gaussianSD)**2) for x in degreeAxis])
						
	#The code below is the proper way to do this using Von Mises, but this doesnt currently allow us to change the spread easily 
	#since I0_kappa cannot be solved for in this version of python.
#	kappa = 5
#	I0_kappa = 27.2399
#	kappaNorm = 0.8671
#	normalizer = 1 / (2*np.pi*I0_kappa) * 1/kappaNorm # last term makes it so max value of pdf is 1 when x=mu. (no longer integrates to 1)
#	term = 255*np.array([np.exp(kappa*np.cos((x-mean)*np.pi/180)) for x in degreeAxis])
#	circularGaussian = normalizer * term
						
	return circularGaussian


def chooseSignal(motorIntensities):
	'''
	Determines which signal to send - standard signal, stop or belt off
	'''
	global stopSignal, beltOffSignal, hitWaypoint, sendStopSignal, stopTimer, onTimer, onTime
	
	#If subject just hit waypoint, start sending the 'stop' signal
	if hitWaypoint:
		dataToSend = stopSignal 
		
		#Reset variables and timers
		hitWaypoint = False
		stopTimer = tm.time()
		timer = tm.time() - 1.1*constants.WRITE_PERIOD;
		
	
	#If the stop signal hasn't lasted long enough yet, keep sending it
	elif sendStopSignal:
		dataToSend = stopSignal

		#If stop signal has lasted long enough, change back to standard signal
		if tm.time() - stopTimer >= constants.STOP_TIME:
			#Set data to the intensity signal
			dataToSend = [constants.MSG_START] + motorIntensities + [constants.MSG_END]
			
			#Rest variables and timers 
			sendStopSignal = False
			timer = tm.time() - 1.1*constants.WRITE_PERIOD; 
			onTimer = tm.time()
			
	
	#If the stop signal is not active, send the standard signal for onTime seconds 
	elif tm.time() - onTimer <= onTime:
		dataToSend = [constants.MSG_START] + motorIntensities + [constants.MSG_END]
		
	#For the rest of the control period, send the belt-off signal 
	else:
		dataToSend = beltOffSignal
		
		#Reset onTimer after a full period has passed
		if tm.time() - onTimer >= constants.CONTROL_PERIOD:
			onTimer = tm.time()
	
	return dataToSend 
	



def checkTimers(curPos,curRot):
	'''
	Resets the buffers, records positional and orientational data and checks if final checkpoint has been reached
	'''
	global ser,recordTimer, bufferTimer, recordPos, recordOrient, waypointCounter, beltOffSignal
	
	# Records positional and orientational data at regular intervals 
	if tm.time() - recordTimer > constants.RECORD_TIME:
		recordPos = np.append(recordPos, curPos) ; recordOrient = np.append(recordOrient, curRot)
		recordTimer = tm.time()
	
	#Reset buffers every at regular intervals
	if tm.time() - bufferTimer > constants.BUFFER_RESET_TIME:
#		ser.reset_input_buffer()
#		ser.reset_output_buffer()
		bufferTimer = tm.time()



def resetTrial():
	'''
	Saves the data for the current path and prepares for next path
	'''
	global pathTime, timer, onTimer, stopTimer, bufferTimer, recordTimer, recordPos, recordOrient, waypointCounter, \
			hitWaypoint, sendStop, waypoints, pathCounter, reorient, atPoleToGoTo, onTime, totalPaths

	#Save data with all important information in file name
	if constants.CONTROL_PERIOD == onTime:
		scheme = '_continuous_'
	else:
		scheme = '_discrete_'
	
	if warmup:
		string = 'warmup_'
	else:
		string = str(numMotors)+'mtr_'
	
	dataFile = open('Loc_'+string+vibrationType+scheme+'sub'+str(subID)+'_'+'path'+str(pathCounter)+'.txt','w+')
	dataFile.write(",".join(str(data) for data in recordPos)) #Save position data to first line
	dataFile.write('\n')
	dataFile.write(",".join(str(data) for data in recordOrient)) #Save orientation data to second line 
	dataFile.write('\n')
	dataFile.write(str(pathTime))
	dataFile.close()
	
	#np.save(string+vibrationType+scheme+'sub'+str(subID)+'_'+'path'+str(pathCounter)+'_pos.npy', recordPos)
	#np.save(string+vibrationType+scheme+'sub'+str(subID)+'_'+'path'+str(pathCounter)+'_ori.npy', recordOrient)
	
	#Send stop signal
#	for num in stopSignal:
#		ser.write(struct.pack('>B', num))
	
	tm.sleep(2*constants.STOP_TIME)
	
	#Turn off motors at the end
#	for num in beltOffSignal:
#		ser.write(struct.pack('>B', num))
		
	print(stopSignal)
	

	#Exit system once all trials are complete, or restart orientation and load next path  
	if pathCounter ==  totalPaths:
		sys.exit(0)
	
	else:
		#Increment trial counter
		pathCounter += 1
		
		#Assign next path (needs to be implemented still)
		waypoints = setNextPath()
		
		#Enter reorientation mode
		reorient = True 
		
		#Show reorientation poles
		poleToFace.visible(viz.ON)
		poleToGoTo.visible(viz.ON)
		
		compassNeedle.visible(viz.OFF) #hide compass
		text_score.visible(viz.OFF) #hide orientation info 
		
		atPoleToGoTo = False
		
		
		
#End of code 		
###################################################################################################################















