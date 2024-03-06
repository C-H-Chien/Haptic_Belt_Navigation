#########################################################################################################################
# Imports
from pygame.locals import *
import pygame, sys, math, random, numpy as np
import time as tm, serial, struct, random
import constants as c

##########################################################################################################################


def runRelIntensityTest(port,numMotors, subID):
    """
    Initiates a new relative intensity test
    """
    global constants, scr, mySmallFont, myBigFont, start_time, cache_time, absStartTime, ser, vibrationCount, keyPressed, testStarted, \
        motorIntensities, subjectResponse, strengthLeft, strengthRight, intensityPairs, warmup

    #Initialize constants class
    constants = c.constants()

    #Initialize variables and Pygame Parameters
    start_time = tm.time()
    ser = serial.Serial(port)
    ser.baudrate = constants.SERIAL_BAUDRATE
    pygame.init()
    pygame.display.set_caption('Relative Haptic Intensity Test')

    mySmallFont = pygame.font.SysFont('monospace', 18)
    myBigFont = pygame.font.SysFont('monospace', 50)
    beltOffSignal = [constants.MSG_START] + numMotors * [0] + [constants.MSG_END]

    #Determine intensity pairs and trial order
    intensityPairs = constants.WARMUP_INTENSITIES + generatePairs()

    # Initialize other parameters
    resetTest(port, numMotors)
    currIntensityPair = intensityPairs[vibrationCount]


    #Loop through all pairs
    while True:

        #Update trial based on max trial time or if the subject has pressed one of the relevant keys
        if (tm.time() - start_time >= constants.MAX_TRIAL_DURATION or keyPressed) and testStarted:

            #If the full trial time expired without a response, save 'None' as the subject response
            if tm.time() - start_time > constants.MAX_TRIAL_DURATION:
                trackData(currIntensityPair,None)

            #Adjust variables and reset timer
            keyPressed = False
            vibrationCount += 1
            start_time = tm.time()

            if vibrationCount >= len(constants.WARMUP_INTENSITIES) and warmup:
                warmup = False

            #Check if all vibrations have been tested
            if vibrationCount >= len(intensityPairs):
                #Turn off belt
                for num in beltOffSignal:
                    ser.write(struct.pack('>B', num))

                #Save data and exit system with a new line for each of the four data streams
                dataFile = open('RelInt_sub'+str(subID)+'.txt','w+')
                dataFile.write(",".join(str(data) for data in subjectResponse))  #Save subject's response
                dataFile.write('\n')
                dataFile.write(",".join(str(data) for data in strengthLeft))  #Save left motor data
                dataFile.write('\n')
                dataFile.write(",".join(str(data) for data in strengthRight))  #Save right motor data
                dataFile.write('\n')
                dataFile.write(",".join(str(data) for data in subjectTimes)) # Save right motor data
                dataFile.write('\n')
                dataFile.write(str(tm.time()-absStartTime)) #Save total experiment time
                dataFile.close()

                #Close pygame
                pygame.quit()
                sys.exit()

            #Update data sent to the belt
            currIntensityPair = intensityPairs[vibrationCount]
            motorIntensities[constants.LEFT_MOTOR] = currIntensityPair[0]
            motorIntensities[constants.RIGHT_MOTOR] = currIntensityPair[1]
            dataToSend = [constants.MSG_START] + motorIntensities + [constants.MSG_END]

            #Send data to belt
            for num in dataToSend:
                ser.write(struct.pack('>B', num))


        #Update display if test has been started by subject
        if testStarted:
            updateDisplay(vibrationCount)

        #Periodically flush the serial buffer
        if tm.time() - cache_time > constants.BUFFER_RESET_TIME:
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            cache_time = tm.time()

        #Check if any events took place
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.KEYDOWN:

                #Start the test once the subject presses space
                if not testStarted and event.key == pygame.K_SPACE:
                    start_time = tm.time()
                    absStartTime = tm.time()
                    testStarted = True

                #Save data based on subject's response following a button press only if they have started the test
                if testStarted:
                    #'S' key represents both motors having the same perceived intensity
                    if event.key == pygame.K_s:
                        trackData(currIntensityPair,constants.SAME)
                        keyPressed = True

                    #'A' key represents left motor having higher perceived intensity
                    elif event.key == pygame.K_a:
                        trackData(currIntensityPair,constants.LEFT)
                        keyPressed = True

                    #'D' key represents right motor having higher perceived intensity
                    elif event.key == pygame.K_d:
                        trackData(currIntensityPair,constants.RIGHT)
                        keyPressed = True

                    #'W' key represents no vibration felt on either motor
                    elif event.key == pygame.K_w:
                        trackData(currIntensityPair,constants.NEITHER)
                        keyPressed = True

                    #'P' - resets the test if needed (simpler than ending and rerunning the code manually)
                    elif event.key == pygame.K_p:
                        resetTest(port,numMotors)


def generatePairs():
    """
    Returns a shuffled list of combinations to vibrate
    """
    '''
    3 VERY HIGH-VARIATION: |VID| > 192
    3 HIGH-VARIATION: 128 < |VID| <= 192
    3 MID-VARIATION: 77 < |VID| <= 128
    3 LOW-VARIATION: 51 < |VID| <= 77
    2 SIMILAR(A): 38 < |VID| <= 51
    2 SIMILAR(B): 26 < |VID| <= 38
    2 VERY SIMILAR(A): 13 < |VID| <= 26
    2 VERY SIMILAR(B): 0 < |VID| <= 13
    2 IDENTICAL: |VID| = 0
    '''
    global constants

    #Generate the intensity combinations by iterating through the bins outlined above (stored in constants class)
    intensityPairs = []
    for bin in constants.BINS:
        for trial in range(constants.REPS*bin[0]):
            intensityPairs.append(chooseIntensities(bin[1], bin[2]))

    #Shuffle the intensity combinations so they appear in random order
    random.shuffle(intensityPairs)

    return intensityPairs


def chooseIntensities(lowThresh, highThresh):
    """
    Returns a tuple of left and right vibration intensities within specified tuple range
    """
    #Randomly choose intensity difference between the motors
    intensityDiff = random.randint(lowThresh, highThresh)

    #Randomly assign motor intensities with correct intensity difference
    intensity1 = random.randint(0, 255-intensityDiff)
    intensity2 = intensity1 + intensityDiff

    #Randomly choose which motor receives which intensity and return the intensities
    if random.randint(1,2) == 1:
        return (intensity1, intensity2)
    else:
        return (intensity2, intensity1)


def initializeDisplay():
    """
    Initializes the display before the experiment begins
    """
    global scr, subscr

    #Define variables for label locations used in updateDisplay()
    instructLabel0 = mySmallFont.render(constants.INSTRUCTIONS[0], 1, constants.INSTRUCTIONS_COLOR)
    instructLabel1 = mySmallFont.render(constants.INSTRUCTIONS[1], 1, constants.INSTRUCTIONS_COLOR)
    instructLabel2 = mySmallFont.render(constants.INSTRUCTIONS[2], 1, constants.INSTRUCTIONS_COLOR)
    instructLabel3 = mySmallFont.render(constants.INSTRUCTIONS[3], 1, constants.INSTRUCTIONS_COLOR)
    instructTextSize = mySmallFont.size(constants.INSTRUCTIONS[0])
    instructLabelX = int(constants.DISPLAY_SIZE[0] / 2 - instructTextSize[0] / 2)
    instructLabelY = int(2 * constants.DISPLAY_SIZE[1] / 3 - instructTextSize[1] / 2)

    #Initialize starting screen
    scr = pygame.display.set_mode(constants.DISPLAY_SIZE)
    scr.fill(constants.BACKGROUND_COLOR)

    # Add subscreen at top 8th of the screen where the changing label will go
    subscr = scr.subsurface(pygame.Rect(0, 0, constants.DISPLAY_SIZE[0], int(3*constants.DISPLAY_SIZE[1]/5)))

    startTextSize = myBigFont.size(constants.START_TEXT)
    startLabel = myBigFont.render(constants.START_TEXT, 1, (255,0,0))
    subscr.blit(startLabel, (int(constants.DISPLAY_SIZE[0]/2 - startTextSize[0]/2), int(constants.DISPLAY_SIZE[1]/2 - startTextSize[1]/2)))
    scr.blit(instructLabel0, (instructLabelX, instructLabelY))
    scr.blit(instructLabel1, (instructLabelX, instructLabelY + constants.LABEL_SEPARATION))
    scr.blit(instructLabel2, (instructLabelX, instructLabelY + 2*constants.LABEL_SEPARATION))
    scr.blit(instructLabel3, (instructLabelX, instructLabelY + 3*constants.LABEL_SEPARATION))

    pygame.display.update()



def updateDisplay(vibrationCount):
    '''
    Updates the display that the subject sees
    '''
    global scr, subscr, myBigFont, start_time, intensityPairs

    #Reload the screen
    subscr.fill(constants.BACKGROUND_COLOR)
    vibText = "Vibration "+str(vibrationCount+1)+"/"+str(len(intensityPairs))+": "+str(max(0.0,round(start_time +
                                                                            constants.MAX_TRIAL_DURATION-tm.time(),1)))+"s"
    vibTextSize = myBigFont.size(vibText)

    #Make guiding label
    vibLabel = myBigFont.render(vibText, 1, constants.TEXT_COLORS[vibrationCount % len(constants.TEXT_COLORS)])

    #Reload labels to keep them displayed (have to this everytime?? Seems unnecessary but doesnt work otherwise)
    subscr.blit(vibLabel, (int(constants.DISPLAY_SIZE[0]/2 - vibTextSize[0]/2), int(constants.DISPLAY_SIZE[1]/2 - vibTextSize[1]/2)))

    pygame.display.update()


def resetTest(port,numMotors):
    """
    Restarts the test without needing to rerun the code
    """
    global start_time, cache_time, vibrationCount, keyPressed, testStarted, motorIntensities, subjectResponse,\
        strengthLeft, strengthRight, warmup, subjectTimes

    #Reset variables
    cache_time = tm.time()
    vibrationCount = 0
    keyPressed = False
    testStarted = False
    warmup = True
    if len(constants.WARMUP_INTENSITIES) is 0:
        warmup = False
    motorIntensities = numMotors * [0]  # Initialize all motors to intensity 0

    #Reset data arrays
    subjectResponse = [] #Stores the subject's choice
    strengthLeft = []
    strengthRight = []
    subjectTimes = []

    #Initialize display to starting screen
    initializeDisplay()

def trackData(currIntensityPair, response):
    """
    Saves data to the respective array's based on the subject's response
    """
    global strengthLeft, strengthRight, subjectResponse,warmup, vibrationCount, start_time
    #Only save data after first warmup set is completed
    if not warmup:
        strengthLeft.append(currIntensityPair[0])
        strengthRight.append(currIntensityPair[1])
        subjectResponse.append(response)
        subjectTimes.append(round(tm.time()-start_time,2))


#########################################################################################################################

runRelIntensityTest('COM7',12,1)

#End of code
#########################################################################################################################

