'''
The purpose of this script is to run acuity tests for vibration intensities.
First, we set up a Pygame window, and define several time-control variables.
At each decision, two adjacent motors will vibrate at different vibration
intensities. It is the job of of the subject to select on the Pygame window
which motor is vibrating at a higher intensity. After 20 trials, the experiment
will end.
'''
# Imports
from pygame.locals import *
import pygame, sys, math, numpy as np
import time as tm, serial, struct, random


# Sets up Pygame Parameters
pygame.init()
scr = pygame.display.set_mode((720, 720))
myfont = pygame.font.SysFont('monospace', 24)
# Sets up variables
absolute_start = tm.time()
start_time = tm.time() ; cache_time = tm.time()
ser = serial.Serial('/dev/tty.usbmodem1301')
ser.baudrate = 115200
colors = [(255, 255, 255), (0,255,0), (0,0,255)]
vibrationCount = 0 ; runCount = -1
# Here, if left is stronger: 0, if right is stronger: 1
guessedStrength = np.array([])
strengthLeft = np.array([]) ; strengthRight = np.array([])

# CHANGE THIS TO CHANGE THE NUMBER OF MOTORS IN THE BELT (8 OR 12)
# ------------
numMotors = 12
# ------------

# Defines all possible combinations of different vibration intensities
combos = [(0,5), (0,4), (0,3), (0,2), (0,1), (1,5), (1,4), (1,3), (1,2), (2,5), (2,4), (2,3), (3,5), (3,4), (4,5),
(5,0),(4,0),(3,0),(2,0),(1,0),(5,1), (4,1), (3,1), (2,1), (5,2), (4,2), (3,2), (5,3), (4,3), (5,4)]
random.shuffle(combos)
intensities = combos[runCount]
while True:
    # Handles the visual display on the screen
    # --------------------------------------------------------------------------
    pygame.display.update() ; scr.fill((0, 0, 0))
    # Prints "New Vibration" at the top of the screen (color changes with new vibration)
    labelNew = myfont.render("New Vibration", 1, colors[vibrationCount % 3])
    scr.blit(labelNew, (310, 100))
    labelInstruct = myfont.render("Press 'a' if left vibration is stronger",
    1, colors[vibrationCount % 3])
    scr.blit(labelInstruct, (310, 200))
    labelInstruct2 = myfont.render("Press 'd' if right vibration is stronger",
    1, colors[vibrationCount % 3])
    scr.blit(labelInstruct2, (310, 250))
    # --------------------------------------------------------------------------
    if tm.time() - start_time > 5:
        runCount += 1 ; vibrationCount += 1
        if runCount >= len(combos):
            ser.write(struct.pack('>B', 255))
            np.save('vibeguess.npy', guessedStrength)
            np.save('leftStrength.npy', strengthLeft)
            np.save('rightStrength.npy', strengthRight)
            pygame.quit()
            sys.exit()
        #intensities = combos[runCount]
        directionsToSend = [255]
        if intensities[0] == 5:
            directionsToSend.append(2)
        elif intensities[1] == 5:
            directionsToSend.append(3)
        directionsToSend.append(254)
        if intensities[0] == 4:
            directionsToSend.append(2)
        elif intensities[1] == 4:
            directionsToSend.append(3)
        directionsToSend.append(253)
        if intensities[0] == 3:
            directionsToSend.append(2)
        elif intensities[1] == 3:
            directionsToSend.append(3)
        directionsToSend.append(252)
        if intensities[0] == 2:
            directionsToSend.append(2)
        elif intensities[1] == 2:
            directionsToSend.append(3)
        directionsToSend.append(251)
        if intensities[0] == 1:
            directionsToSend.append(2)
        elif intensities[1] == 1:
            directionsToSend.append(3)
        directionsToSend.append(250)
        for num in directionsToSend:
            ser.write(struct.pack('>B', num))
        start_time = tm.time()

    # Every 10 seconds, we flush the serial buffer
    if tm.time() - cache_time > 10:
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        cache_time = tm.time()

    # Records the press of either "a" or "d" keys that signify
    # a stronger vibration on the left or right respectively.
    ev = pygame.event.get()

    for event in ev:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                strengthLeft = np.append(strengthLeft, intensities[0])
                strengthRight = np.append(strengthRight, intensities[1])
                guessedStrength = np.append(guessedStrength, 0)
            elif event.key == pygame.K_d:
                strengthLeft = np.append(strengthLeft, intensities[0])
                strengthRight = np.append(strengthRight, intensities[1])
                guessedStrength = np.append(guessedStrength, 1)

################################################################################
################################################################################
################################################################################
'''
EOF
'''
