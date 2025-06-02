###########################################################################################################################
# Imports
from pygame.locals import *
import pygame, sys, math, random, numpy as np
import time as tm, serial, struct
import constants as c
from collections import Counter
import tkinter as tk
import sys, math, random, numpy as np
import time as tm, struct
from scale_gui import get_subject_id, main_scaling


###########################################################################################################################

response = [0,1]

def runDirectionTest(port, numMotors, subID):
   global constants, ser, startTime, absStartTime, cacheTime, mySmallFont, myBigFont, vibrationCount, \
       stopSignal, beltOffSignal, angles, testStarted, warmup, hasClicked, degreeAxis, lastClickTime, currAngle, responseRecorded


   constants = c.constants()
   ser = serial.Serial(port, timeout=0.1)
   ser.baudrate = constants.SERIAL_BAUDRATE
   pygame.init()
   pygame.display.set_caption('Relative Haptic Intensity Test')


   beltOffSignal = [constants.MSG_START] + numMotors * [0] + [constants.MSG_END]
   stopSignal = [constants.MSG_START] + numMotors * [255] + [constants.MSG_END]

   #angles = [(0, 0), (0, 0), (0, 0), (0, 0), (270, 0), (90, 0), (45, 0)]
   angles = generateAngles(11)
   #print(angles)
#    exit(0)
   print("Total trials = " + str(len(angles)))


   resetTest(port, numMotors)
   vibrationCount = 0
   validClick = True
   motorOnTime = None  # Tracks when motors were last turned on
   responseTimeout = None  # Timer for user response
   responseRecorded = False  # To check if a response was recorded during the vibration period
   acceptClick = False


   while True:

       current_time = tm.time()
      
       # Turn off motors after 3 seconds
       if motorOnTime and current_time - motorOnTime >= 2:
           updateBelt('OFF', numMotors) 
           acceptClick = True


       # Begin the next motor vibration after 1 second of slack time
       if responseTimeout and current_time - responseTimeout >= 1:
           if vibrationCount < len(angles):
               currAngle = angles[vibrationCount]
            #    updateBelt(currAngle, numMotors)
               print(response[0])
               updateBelt((response[0], 0), numMotors)
               print("current angle is: " + str(currAngle) + ", viberation count is: " + str(vibrationCount))
               motorOnTime = current_time  # Restart motor timing for 3 seconds
               responseTimeout = None  # Reset response timer
               responseRecorded = False  # Reset response flag for next cycle
               vibrationCount += 1
               acceptClick = False
           else:
               recordData(numMotors, subID)
               print('data recorded\n')


       ev = pygame.event.get()
       for event in ev:
           if event.type == pygame.KEYDOWN:
               if not testStarted and event.key == pygame.K_SPACE:
                   startTime = tm.time()
                   absStartTime = tm.time()
                   testStarted = True


                   vibrationCount = 0
                   currAngle = angles[vibrationCount]
                #    print(currAngle)
                #    updateBelt(currAngle, numMotors)
                   print(response[0])
                   updateBelt((response[0], 0), numMotors)
                   print("current angle is: " + str(currAngle) + ", viberation count is: " + str(vibrationCount))
                   motorOnTime = current_time  # Restart motor timing for 2 seconds
                   responseTimeout = None  # Reset response timer
                   vibrationCount += 1
                   acceptClick = False
                   responseRecorded = False  # Reset response flag for next cycle


           elif event.type == pygame.QUIT:
               updateBelt('OFF', numMotors)
               pygame.quit()
               sys.exit()


           elif event.type == pygame.MOUSEBUTTONUP and not hasClicked and testStarted:
               if acceptClick and current_time - lastClickTime >= constants.MIN_CLICK_DELAY:
                   pos = pygame.mouse.get_pos()
                   validClick = checkClick(pos)
                   lastClickTime = tm.time()
                   if validClick:
                       hasClicked = True
                       responseRecorded = True  # Set the flag to true if a valid click was recorded
               else:
                   print("invalid click")


           if hasClicked and testStarted:
               print("valid click detected")
               hasClicked = False
               responseTimeout = current_time  # Wait for 1 second before starting the next motor
               acceptClick = False
               motorOnTime = None  # Reset the motor timer
               updateBelt('OFF', numMotors)

       if testStarted:
           updateDisplay(vibrationCount, validClick)
          

       if tm.time() - cacheTime > constants.BUFFER_RESET_TIME:
           ser.reset_input_buffer()
           ser.reset_output_buffer()
           cacheTime = tm.time()



def recordData(numMotors, subID):
   for num in beltOffSignal:
       ser.write(struct.pack('>B', num))


   # Save data and exit system with a new line for each of the four data streams
   dataFile = open('DirPer_'+ str(numMotors) + 'mtr_sub' + str(subID) + '_singleImpulse.txt', 'w+')
   dataFile.write(",".join(str(data) for data in subjectResponse))  # Save subject's response
   dataFile.write('\n')
   dataFile.write(",".join(str(data) for data in angles))  # Save angle and vibration type
   dataFile.write('\n')
   dataFile.write(",".join(str(data) for data in subjectTimes))  # Save time stamps
   dataFile.write('\n')
   print(round(tm.time()-absStartTime,2))
   dataFile.write(str(round(tm.time()-absStartTime,2)))  # Save total experiment time
   dataFile.close()


   # Close pygame
   pygame.quit()
   experiment_type = "impulse"
   main_scaling(subID, experiment_type)
   sys.exit()




def generateAngles(numMotors):
   """
   Returns a 2D array of directions. The first element corresponds to the angle, the second corresponds to the vibration scheme:
   0 - single motor, 1 - Gaussian
   """
   global constants
   angles = []


   shuffled_sequence = generate_sequence(numMotors, 1)
   result = check_repetitions(shuffled_sequence, 1)
   print(f"All elements have exactly 10 repetitions: {result}")
   for angle in shuffled_sequence:
       angles.append((angle*22.5, 0))  # Tuple (angle, scheme)
   return angles


def check_repetitions(arr, required_repetitions=10):
   # Count the occurrences of each element in the array
   counts = Counter(arr)
  
   # Check if all elements have the required number of repetitions
   for count in counts.values():
       if count != required_repetitions:
           return False
   return True




def valid_placement(sequence, num):
   if sequence:
       # Check last number in the sequence
       if len(sequence) > 0 and abs(sequence[-1] - num) <= 1:
           return False
       # Check the second to last number if possible to avoid cycling the first and last numbers
       if len(sequence) == 159 and abs(sequence[0] - num) <= 1:
           return False
   return True




def generate_sequence(n, repetitions):
   sequence = []
   # Create a dictionary to keep track of the count of each number
   num_counts = {i: repetitions for i in range(n)}
   available_numbers = [i for i in range(n) for _ in range(repetitions)]


   while available_numbers:
       random.shuffle(available_numbers)  # Shuffle to try different numbers randomly
       placed = False
       for num in available_numbers:
           if valid_placement(sequence, num) and num_counts[num] > 0:
               sequence.append(num)
               num_counts[num] -= 1
               available_numbers.remove(num)
               placed = True
               break
       if not placed:
           # Reset the sequence if stuck and start over
           sequence = []
           num_counts = {i: repetitions for i in range(n)}
           available_numbers = [i for i in range(n) for _ in range(repetitions)]


   return sequence






def resetTest(port,numMotors):
   """
   Restarts the test without needing to rerun the code
   """
   global cacheTime, vibrationCount, hasClicked, testStarted, subjectResponse,subjectTimes, motorIntensities, \
       beltOffSignal, lastClickTime




   #Reset variables
   cacheTime = tm.time()
   lastClickTime = tm.time()
   vibrationCount = 0
   hasClicked = False
   testStarted = False


   #Start with belt off
   for num in beltOffSignal:
       ser.write(struct.pack('>B', num))


   #Reset data arrays
   subjectResponse = [] #Stores the subject's choice
   subjectTimes = [] #Stores time for each trial


   #Initialize display to starting screen
   initializeDisplay(numMotors)




def initializeDisplay(numMotors):
   """
   Initializes the display before the experiment begins
   """
   global scr, subscr, mySmallFont, myMediumFont, myBigFont, outerCirc, innerCirc, stopRect, offRect, imgRect


   #Initialize screen
   scr = pygame.display.set_mode(constants.DISPLAY_SIZE)
   scr.fill(constants.BACKGROUND_COLOR_DIR)


   #Add subscreen at top 8th of the screen where the changing label will go
   subscr = scr.subsurface(pygame.Rect(0, 0,constants.DISPLAY_SIZE[0],int(constants.DISPLAY_SIZE[1]/8)))


   #Define different fonts
   mySmallFont = pygame.font.SysFont('monospace', 18)
   myBigFont = pygame.font.SysFont('monospace', 50)
   myMediumFont = pygame.font.SysFont('monospace', 28)


   #Draw Display, starting with outer circle
   outerCirc = pygame.draw.circle(scr, constants.CIRCLE_COLOR, (int(constants.DISPLAY_SIZE[0]/2),
                                                    int(constants.DISPLAY_SIZE[1]/2)+constants.CIRCLE_SHIFT), constants.OUTER_RAD)

   #Add lines to and markers to indicate angles
   for angle in np.linspace(-360/2/numMotors, 360-360/2/numMotors, numMotors+1, True):
       x = constants.OUTER_RAD*math.sin(angle*math.pi/180)
       y = constants.OUTER_RAD*math.cos(angle*math.pi/180)
       start = (outerCirc.center[0],outerCirc.center[1])
       end = (-x+outerCirc.center[0],-y+outerCirc.center[1])
       #end = (outerCirc.center[0],outerCirc.center[1])
       color = constants.BACKGROUND_COLOR_DIR


       pygame.draw.line(scr, color, start, end, 5)


   #Draw inner circle
   innerCirc = pygame.draw.circle(scr, constants.BACKGROUND_COLOR_DIR, outerCirc.center, constants.INNER_RAD)


   #Add top-down human view image
   img = pygame.image.load('top_view_img.png').convert()
   img = pygame.transform.scale(img,(330, 274)) #Img size is normally 165, 137
   imgRect = img.get_rect()
   imgRect.center = outerCirc.center
   scr.blit(img,imgRect)


   #Add text labels
   startTextSize = myBigFont.size(constants.START_TEXT)
   startLabel = myBigFont.render(constants.START_TEXT, 1, (255, 0, 0))
   subscr.blit(startLabel, (int(constants.DISPLAY_SIZE[0]/2 - startTextSize[0]/2), int(constants.DISPLAY_SIZE[1]/11 - startTextSize[1]/2)))


   pygame.display.update()






def updateDisplay(vibrationCount, validClick):
   '''
   Updates the subsurface at the top of the display
   '''
   global subscr, startTime, angles
   subscr.fill(constants.BACKGROUND_COLOR_DIR)
   if validClick:
       vibText = "New Vibration, please select a point on the circle."
       vibTextSize = myMediumFont.size(vibText)
       # Make guiding label
       vibLabel = myMediumFont.render(vibText, 1, constants.TEXT_COLORS[vibrationCount % len(constants.TEXT_COLORS)])
   else:
       vibText = "Invalid click location, please click on the circle!"
       vibTextSize = myMediumFont.size(vibText)
       # Make guiding label
       vibLabel = myMediumFont.render(vibText, 1, (0, 0, 0))


   # Reload labels to keep them displayed (have to this everytime?? Seems unnecessary but doesnt work otherwise)
   subscr.blit(vibLabel, (int(constants.DISPLAY_SIZE[0]/2-vibTextSize[0]/2), int(constants.DISPLAY_SIZE[1]/11-vibTextSize[1]/2)))


   pygame.display.update()






def trackData(response):
   """
   Saves data to the respective array's based on the subject's response
   """
   global subjectResponse, subjectTimes, absStartTime


   subjectResponse.append(response)
   subjectTimes.append(round(tm.time()-absStartTime,2))
   #print(round(tm.time()-absStartTime,2))




def updateBelt(currAngle, numMotors):
#    currAngle = (response, 0)
   if currAngle == 'OFF':
       dataToSend = [constants.MSG_START] + numMotors * [0] + [constants.MSG_END]
  
   #Otherwise, determine which scheme to use and generate motor intensities
   else:
       if currAngle[1] == 0: #single motor scheme
           motorIntensities = numMotors * [0]
           # Determine closest motor and set its intensity to 100%
           motorToActivate = int(round(currAngle[0]/(360/numMotors)))%numMotors  # %numMotors prevents edge cases where this rounds to numMotors
           motorIntensities[motorToActivate] = 250
       else:
           print("Scheme code not recognized")


       #print(len(motorIntensities))
       motorIntensities.reverse()
       if numMotors != 8:
           motorIntensities1 = [motorIntensities[len(motorIntensities)-1]] + motorIntensities[0:len(motorIntensities)-1]
       else:
           motorIntensities1 = motorIntensities
       dataToSend = [constants.MSG_START] + motorIntensities1 + [constants.MSG_END]
       #print(dataToSend)




   #Send data to belt
   for num in dataToSend:
       ser.write(struct.pack('>B', num))






def wrapTo180(angleError):
   '''
   Returns input angleError as an angle between -180 and 180
   '''
   if angleError > 180:
       angleError -= 360
   elif angleError < -180:
       angleError += 360
   return angleError






def checkClick(pos):
   """
   Analyzes the click location and saves data with the appropriate response if relevant
   """
   global innerCirc, outerCirc, stopRect, offRect, hasClicked


   #Check location of click
   circCenter = innerCirc.center
   circleEqn = (pos[0]-circCenter[0])**2 + (pos[1]-circCenter[1])**2
   clickInCircle = circleEqn <= constants.OUTER_RAD**2 and circleEqn >= constants.INNER_RAD**2


   # Update boolean
   hasClicked = True
   saveData = True


   if clickInCircle:


       #Use trig to find angle (add 90 to adjust for diagram orientation)
       angle = (math.atan2(pos[1]-circCenter[1],pos[0]-circCenter[0])*180/math.pi) + 90


       #Wrap angles as needed
       if angle >= 360:
           angle -= 360
       elif angle <= -0:
           angle += 360
       response[0] = round(angle,1)


   else:
       hasClicked = False #Dont count invalid clicks
       saveData = False #Dont save data
       print('Invalid click location')


   #Save data if the click was valid
   if saveData:
       trackData(response[0])
       print("Response angle: " + str(response[0]))


   return saveData




########################################################################################################################
def main():
   # Initialize GUI for Subject ID
   subID = get_subject_id()
   if subID is None:
       print("No Subject ID provided.")
       sys.exit(1)


   # Convert subject_id to integer if necessary
   try:
       subID = int(subID)
   except ValueError:
       print("Invalid Subject ID. Please enter a valid integer.")
       sys.exit(1)


   # Define the port and number of motors
   port = '/dev/tty.usbmodem101' #1101
   numMotors = 16  # The number of motors present on the haptic belt


   # Call the function to start the test
   runDirectionTest(port, numMotors, subID)




if __name__ == "__main__":
   main()
#########################################################################################################################





