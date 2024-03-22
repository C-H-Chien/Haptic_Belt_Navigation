import locomotion
import numpy as np

###########################################################################################################
# Define variables
port = 'COM4'					#Port for communication 
showHelpers = True  			#Boolean to determine if compass and angle label are shown. Set to false for actual tests 

#############################################################################################################
		
numMotors = 12  					#Number of motors on the belt
subID = 1						#Subject ID, needs to be a number (just used for saving data)
warmup = True 				    #Set to true for first run with subject. This runs the 4 warmup trials 
								#(single/continuous, then single/discrete, then gaussian/continous, then gaussian/discrete)


##########################################################################################################
locomotion.runLocomotionSimulation(port, numMotors, showHelpers, subID, warmup)