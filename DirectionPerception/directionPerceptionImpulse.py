###########################################################################################################################
# Imports
from pygame.locals import *
import pygame, sys, math, random, numpy as np
import time as tm, serial, struct
import constants as c

###########################################################################################################################


def runDirectionTest(port,numMotors, subID):
    """
    Initiates a new relative intensity test
    """
    global constants, ser, startTime, absStartTime, cacheTime, mySmallFont, myBigFont, vibrationCount, \
        stopSignal, beltOffSignal, angles, testStarted, hasClicked, degreeAxis, lastClickTime, currAngle

    #Initialize constants class
    constants = c.constants()

    #Initialize variables and Pygame Parameters
    startTime = tm.time()
    ser = serial.Serial(port, timeout=0.1)
    ser.baudrate = constants.SERIAL_BAUDRATE
    pygame.init()
    pygame.display.set_caption('Relative Haptic Intensity Test')

    beltOffSignal = [constants.MSG_START] + numMotors * [0] + [constants.MSG_END]
    stopSignal = [constants.MSG_START] + numMotors * [255] + [constants.MSG_END]

    # Prepare for Gaussian vibration type
    degreeAxis = np.linspace(0, 360, numMotors, False)
    degreeAxis = [wrapTo180(degree) for degree in degreeAxis]

    # Determine intensity pairs and trial order
    angles = generateAngles(numMotors) 
    print("Total trials = " + str(len(angles)))


    # Initialize other parameters
    resetTest(port, numMotors)
    currAngle = angles[vibrationCount]

    # Loop through all directions
    while True:
        
        # Update trial based on max trial time or if the subject has pressed one of the relevant keys
        #if (tm.time() - startTime >= constants.MAX_TRIAL_DURATION_DIR or hasClicked) and testStarted:
        if hasClicked and testStarted:

            # If the full trial time expired without a response, save 'None' as the subject response
            # if tm.time() - startTime > constants.MAX_TRIAL_DURATION:
            #     trackData(None)

            # Adjust variables and reset timer
            hasClicked = False
            vibrationCount += 1
            startTime = tm.time()

            # Check if all vibrations have been tested
            if vibrationCount >= len(angles):
                #Save total time
                # Turn off belt
                for num in beltOffSignal:
                    ser.write(struct.pack('>B', num))

                # Save data and exit system with a new line for each of the four data streams
                dataFile = open('DirPer_'+ str(numMotors) + 'mtr_sub' + str(subID) + '.txt', 'w+')
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
                sys.exit()

            #Update angle
            currAngle = angles[vibrationCount]

            # Update data sent to the belt
            updateBelt(currAngle, numMotors)


        # Update display if test has been started by subject
        if testStarted:
            updateDisplay(vibrationCount)

        # Periodically flush the serial buffer
        if tm.time() - cacheTime > constants.BUFFER_RESET_TIME:
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            cacheTime = tm.time()

        # Check if any events took place
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.KEYDOWN:

                # Start the test once the subject presses space
                if not testStarted and event.key == pygame.K_SPACE:
                    startTime = tm.time()
                    absStartTime = tm.time()
                    updateBelt(currAngle, numMotors)
                    testStarted = True

                # Save data based on subject's response following a button press only if they have started the test
                if testStarted:
                    # 'P' - resets the test if needed (simpler than ending and rerunning the code manually)
                    if event.key == pygame.K_p:
                        resetTest(port, numMotors)

            #Check for mouse clicks
            elif event.type == pygame.QUIT:
                updateBelt(beltOffSignal, numMotors)
                updateBelt(stopSignal, numMotors)
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.MOUSEBUTTONUP and not hasClicked and testStarted:

                #Only register clicks if they dont occur too soon after eachother
                if tm.time() - lastClickTime >= constants.MIN_CLICK_DELAY:
                    pos = pygame.mouse.get_pos()
                    checkClick(pos)
                    lastClickTime = tm.time()


def generateAngles(numMotors):
    """
    Returns a 2D array of directions. The first element corresponds to the angle, the second corresponds to the vibration scheme:
    0 - single motor, 1 - Gaussian
    """
    global constants
    angles = []
    for rep in range(constants.NUM_REPS):
        colAngles = np.linspace(0, 360, numMotors, False)
        for angle in colAngles:
            angles.append((angle,0))
        random.shuffle(angles)
    return angles


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
    initializeDisplay()


def initializeDisplay():
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
    for angle in np.linspace(0, 180, 1, False):
        x = constants.OUTER_RAD*math.sin(angle*math.pi/180)
        y = constants.OUTER_RAD*math.cos(angle*math.pi/180)
        start = (outerCirc.center[0],outerCirc.center[1])
        end = (-x+outerCirc.center[0],-y+outerCirc.center[1])
        #end = (outerCirc.center[0],outerCirc.center[1])
        color = constants.BACKGROUND_COLOR_DIR

        #Make cardinal directions red
        # if angle%90 == 0:
        #     color = (255,0,0)

        pygame.draw.line(scr, color, start, end, 5)

    # #Add lables to some of the angle markers
    # for angle in np.linspace(0,360,2,False):
    #     # Add label
    #     if angle+90 >= 360:
    #         angle -= 360
    #
    #     labelSize = mySmallFont.size(str(int(angle + 90)))
    #     labelX = (constants.ANGLE_LABEL_GAP + constants.OUTER_RAD) * math.cos(angle * math.pi / 180) + \
    #              outerCirc.center[0] - int(labelSize[0]/2)
    #     labelY = (constants.ANGLE_LABEL_GAP + constants.OUTER_RAD) * math.sin(angle * math.pi / 180) + \
    #              outerCirc.center[1] - int(labelSize[1]/2)
    #     angleLabel = mySmallFont.render(str(int(angle + 90)), 1, (255, 0, 0))
    #     scr.blit(angleLabel, (labelX, labelY))

    #Draw inner circle
    innerCirc = pygame.draw.circle(scr, constants.BACKGROUND_COLOR_DIR, outerCirc.center, constants.INNER_RAD)

    # #Draw STOP and BELT OFF buttons
    # stopRect = pygame.Rect((0, 0), (constants.RECT_WIDTH, constants.RECT_HEIGHT))
    # offRect = pygame.Rect((0,0),(constants.RECT_WIDTH, constants.RECT_HEIGHT))
    #
    # stopRect.center = (innerCirc.center[0],innerCirc.center[1]-constants.RECT_SHIFT)
    # offRect.center = (innerCirc.center[0],innerCirc.center[1]+constants.RECT_SHIFT)
    # pygame.draw.rect(scr, (255, 0, 0), stopRect)
    # pygame.draw.rect(scr, (0, 0, 255), offRect)

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

    # stopTextSize = myMediumFont.size(constants.STOP_TEXT)
    # stopLabel = myMediumFont.render(constants.STOP_TEXT,1,(255,255,255))
    # scr.blit(stopLabel, (stopRect.center[0] - stopTextSize[0]/2, stopRect.center[1] - stopTextSize[1]/2))
    #
    # offTextSize = myMediumFont.size(constants.OFF_TEXT)
    # offLabel = myMediumFont.render(constants.OFF_TEXT, 1, (255,255,255))
    # scr.blit(offLabel, (offRect.center[0] - offTextSize[0]/2, offRect.center[1] - offTextSize[1]/2))

    # instructTextSize = mySmallFont.size(constants.INSTRUCT_TEXT)
    # instructLabel = mySmallFont.render(constants.INSTRUCT_TEXT,1,(0,0,0))
    # scr.blit(instructLabel,(innerCirc.center[0] - instructTextSize[0]/2, innerCirc.center[1] - instructTextSize[1]/2))

    pygame.display.update()



def updateDisplay(vibrationCount):
    '''
    Updates the subsurface at the top of the display
    '''
    global subscr, startTime, angles

    subscr.fill(constants.BACKGROUND_COLOR_DIR)
    vibText = "New Vibration"
    vibTextSize = myBigFont.size(vibText)

    # Make guiding label
    vibLabel = myBigFont.render(vibText, 1, constants.TEXT_COLORS[vibrationCount % len(constants.TEXT_COLORS)])

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
    print(round(tm.time()-absStartTime,2))


def updateBelt(currAngle, numMotors):
    """
    Sends data to the belt based on the vibration angle and scheme
    """
    global stopSignal, beltOffSignal

    print("Actual angle " + str(currAngle[0]))

    #Check for STOP and OFF signals first
    if currAngle[0] == 'STOP':
        dataToSend = stopSignal
    elif currAngle[0] == 'OFF':
        dataToSend = beltOffSignal

    #Otherwise, determine which scheme to use and generate motor intensities
    else:
        if currAngle[1] == 0: #single motor scheme
            motorIntensities = numMotors * [0]
            # Determine closest motor and set its intensity to 100%
            motorToActivate = int(round(currAngle[0]/(360/numMotors)))%numMotors  # %numMotors prevents edge cases where this rounds to numMotors
            motorIntensities[motorToActivate] = 250
        else:
            print("Scheme code not recognized")

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
    # clickInStop = stopRect.collidepoint(pos)
    # clickInOff = offRect.collidepoint(pos)

    # Update boolean
    hasClicked = True
    saveData = True
    # if clickInStop:
    #     response = 'STOP'
    # elif clickInOff:
    #     response = 'OFF'
    if clickInCircle:

        #Use trig to find angle (add 90 to adjust for diagram orientation)
        angle = (math.atan2(pos[1]-circCenter[1],pos[0]-circCenter[0])*180/math.pi) + 90

        #Wrap angles as needed
        if angle >= 360:
            angle -= 360
        elif angle <= -0:
            angle += 360
        response = round(angle,1)

    else:
        hasClicked = False #Dont count invalid clicks
        saveData = False #Dont save data
        print('Invalid click location')

    #Save data if the click was valid
    if saveData:
        trackData(response)
        print("Response angle: " + str(response))


########################################################################################################################
def main():
    # Define the port, number of motors, and subject ID
    port = '/dev/tty.usbmodem1101'
    numMotors = 16  # The number of motors present on the haptic belt. 
    subID = 3

    # Call the function to start the test
    runDirectionTest(port, numMotors, subID)


if __name__ == "__main__":
    main()
#End of code
#########################################################################################################################
