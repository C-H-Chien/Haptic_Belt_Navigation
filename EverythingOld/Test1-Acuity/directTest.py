'''
The purpose of this script is to run acuity tests for direct vibrations.
First, we set up a Pygame window, and define several time-control variables.
The number of motors in the belt is then set, and a while loop is implemented
for 150 seconds (29 different vibrations). Note, the first 5 seconds will be
devoted to a forward direction, during which time, the subject should not click

After the initial 5 seconds, a random direction will vibrate every 5 seconds;
the screen will flash a different color when the vibration pattern changes. During
each vibration, the subject should click on the wheel in the direction they
feel is most represented by the vibration.

NOTE: Only one-click per vibration - if not, the data becomes more difficult to parse.
'''

# Imports
from pygame.locals import *
import pygame, sys, math, numpy as np
import time as tm, serial, struct


# Sets up Pygame Parameters
pygame.init()
scr = pygame.display.set_mode((720, 720))
pygame.display.set_caption('Haptic Vibration Test')
myfont = pygame.font.SysFont("monospace", 24)

# Sets up variables
absolute_start = tm.time()
start_time = tm.time() ; buzz_time = tm.time() ; cache_time = tm.time()
direction = 0
ser = serial.Serial('/dev/cu.usbmodem14201')
ser.baudrate = 115200
colors = [(255,255,255),(0,255,0),(0,0,255)]
directionCount = 0 ; hasClicked = True
recordClick = np.array([]) ; recordTime = np.array([]) ; recordDir = np.array([])

# CHANGE THIS TO CHANGE THE NUMBER OF MOTORS IN THE BELT (8 OR 12)
# ------------
numMotors = 12
# ------------

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

# Defines each direction in text (index is consistent)
directions = []
directions.append('north') ; directions.append('north east')
directions.append('east') ; directions.append('south east')
directions.append('south') ; directions.append('south west')
directions.append('west') ; directions.append('north west')
directions.append('stop')


# Game Loop

while True:
    # Handles the visual display on the screen
    # --------------------------------------------------------------------------
    pygame.display.update(); scr.fill((0, 0, 0))
    # Draws concentric circles
    pygame.draw.circle(scr, (255,255,255), (360, 360), 200)
    pygame.draw.circle(scr, (0, 0, 0), (360, 360), 160)
    # Draws dividing lines and stop
    pygame.draw.line(scr, (0, 0, 0), (360, 160), (360, 560), 1)
    pygame.draw.line(scr, (0, 0, 0), (160, 360), (560, 360), 1)
    pygame.draw.line(scr, (0, 0, 0), (360 - 200*np.cos(np.pi / 4), 360 + 200 * np.sin(np.pi / 4)),
    (360 + 200*np.cos(np.pi / 4), 360 - 200*np.sin(np.pi / 4)), 1)
    pygame.draw.line(scr, (0, 0, 0), (360 + 200*np.cos(3*np.pi / 4), 360 - 200 * np.sin(3*np.pi / 4)),
    (360 - 200*np.cos(3*np.pi / 4), 360 + 200*np.sin(3*np.pi / 4)), 1)
    pygame.draw.rect(scr, (255, 0, 0), (300, 300, 120, 120))
    # Writes labels to give guidance
    label0 = myfont.render("0", 1, (150, 150, 150))
    scr.blit(label0, (360 ,140))
    label45 = myfont.render("45", 1, (150, 150, 150))
    scr.blit(label45, ((360 + 10 + 200*np.cos(np.pi / 4), 360 - 15 - 200*np.sin(np.pi / 4))))
    label90 = myfont.render("90", 1, (150, 150, 150))
    scr.blit(label90, ((575, 350)))
    label135 = myfont.render("135", 1, (150, 150, 150))
    scr.blit(label135, ((360 - 5 - 200 * np.cos(3 * np.pi / 4), 360 + 10 - 200 * np.cos(3*np.pi / 4))))
    label180 = myfont.render("180", 1, (150, 150, 150))
    scr.blit(label180, ((355, 570)))
    label225 = myfont.render("225", 1, (150, 150, 150))
    scr.blit(label225, ((180 - np.cos(np.pi / 4)), 360 + 5 +  200*np.sin(np.pi / 4)))
    label270 = myfont.render("270", 1, (150, 150, 150))
    scr.blit(label270, (125, 350))
    label315 = myfont.render("315", 1, (150, 150, 150))
    scr.blit(label315, (180 + 5 - np.cos(np.pi / 4), 180 + 5 - np.cos(np.pi / 4)))
    # Prints "New Direction" at the top of the screen (color changes with each new direction)
    labelNew = myfont.render("New Direction", 1, colors[directionCount % 3])
    scr.blit(labelNew, (310, 100))
    # --------------------------------------------------------------------------

    # Every 5 seconds, a new signal is generated
    if tm.time() - start_time > 5:
        direction = np.random.randint(9)
        recordDir = np.append(recordDir, direction)
        print("New Direction: {}".format(directions[direction]))
        directionCount += 1 ; hasClicked = False
        start_time = tm.time()
    # Every 0.2 seconds, we write to the belt to update the signal at full intensity
    if tm.time() - buzz_time > 0.2:
        ser.write(struct.pack('>B', 255))
        for num in motors[numMotors][direction]:
            ser.write(struct.pack('>B', num))
        ser.write(struct.pack('>B', 254))
        ser.write(struct.pack('>B', 200))
        buzz_time = tm.time()
    # Every 10 seconds, we flush the serial buffer
    if tm.time() - cache_time > 10:
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        cache_time = tm.time()
    # After 250 seconds, the program quits and data is saved
    if tm.time() - absolute_start > 150:
        np.save('positions1.npy', recordClick)
        np.save('times1.npy', recordTime)
        np.save('dirs1.npy', recordDir)
        pygame.quit()
        sys.exit()

    # Records the upclick of a mouse and stores it in the array recordClick
    # Records the time to click after the new signal is updated
    ev = pygame.event.get()

    for event in ev:
        if event.type == pygame.MOUSEBUTTONUP and not hasClicked:
            pos = pygame.mouse.get_pos()
            x = pos[0] ; y = pos[1] ; hasClicked = True
            print(x,y)
            recordClick = np.append(recordClick, (x,y))
            recordTime = np.append(recordTime, tm.time() - start_time)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

################################################################################
################################################################################
################################################################################
'''
EOF
'''
