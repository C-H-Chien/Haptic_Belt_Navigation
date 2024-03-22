import random
import math
import numpy as np
import constants as c 


def prepAllFiles(pathLen, numPathsPerSubPerBelt, numSubs):
	#Makes ALL path files for numSubs subjects 
	for sub in range(1,numSubs+1):
		for numMotors in [8,12,16]:
			#filename = 'Paths_warmups.txt'
			filename = 'Paths_sub' + str(sub) + '_' + str(numMotors) + 'mtr.txt'
			makePathsFile(pathLen,numPathsPerSubPerBelt,filename)
		
		

def makePathsFile(pathLen,numPaths,filename):
	#Creates numPaths paths with length pathLength. These are saved to txt file with each line representing one path
	global constants
	constants = constants.constants()
	pathsFile = open(filename,'w+')
	
	for i in range(numPaths):
		#Generate path and add it to file
		path = generatePath(pathLen)
		pathsFile.write(",".join(str(waypoint)[1:-1] for waypoint in path))
		pathsFile.write('\n')
		
	pathsFile.close()
	


def generatePath(pathLen):
	#Makes a singular path consisting of a list of waypoints
	global constants
	
	path = []
	path.append([0,0,0]) #make first waypoint at origin 
	currLen = 0 #variable to keep track of path length
	
	while currLen < pathLen:
		#Generate x,z coords and find distance from previous waypoint in path
		x = (random.random()*constants.ROOM_X) - constants.ROOM_X/2
		z = (random.random()*constants.ROOM_Z) - constants.ROOM_Z/2
		prevX = path[-1][0] #x coord of previous waypoint
		prevZ = path[-1][2] #z coord of previous waypoint
		addedLen = np.sqrt((x-prevX)**2 + (z-prevZ)**2)
		
		#If length is greater than minimum waypoint separation
		if addedLen >= constants.MIN_WPT_SEP:
			#If path length so far hasnt exceeded pathLen, add waypoint to path
			if currLen + addedLen <= pathLen - constants.MIN_WPT_SEP: #ensures that final waypoint is also atleast MIN_WPT_SEP away 
				path.append([x,0,z]) 
				currLen += addedLen
				
			#Create final waypoint only if the remaining distance is not too large (otherwise randomizing will take a long time)
			elif pathLen - currLen < constants.MAX_LEN:
				#Make final waypoint 
				rad = pathLen-currLen #remaining length needed to complete path
				validWaypointGenerated = False
				
				#Keep generating final waypoint until it is valid 
				while not validWaypointGenerated:
					#Randomly choose point on circle that is rad away from 
					angle = random.random()*360 - 180
					xFinal = rad*math.cos(angle) + prevX
					zFinal = rad*math.sin(angle) + prevZ
					
					#Check that the points are inbound, otherwise keep looping
					if -constants.ROOM_X/2 <= xFinal <= constants.ROOM_X/2  and -constants.ROOM_Z/2 <= zFinal <= constants.ROOM_Z/2:
						path.append([xFinal,0,zFinal])
						currLen += rad
						validWaypointGenerated = True
						
		
	return path

	
	
	
	

prepAllFiles(45,4*5,3) #4*5 - num conditions * num reps per condition
