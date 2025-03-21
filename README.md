## Introduction
This is a joint research on navigation through Haptic Belt from VEN Lab and LEMS Lab at Brown University, advised under Prof. William Warren and Prof. Benjamin Kimia. The project continues the work done by Julian Volleyson and Viktor Ladics in 2020 and 2021, respectively.
## How to wear the belt
For the 8-motor belt, make sure the buckle is on the left side of the waist and arduino box on the right. Battery should be in your back.
## Arduino Setup
Download the code from `Arduino/blunoMaster` and `Arduino/#_MotorBelt_softPWM` to the arduinos connecting to PC side and belt side respectively. Make sure to download the correct .ino code depending on which belt your are using. The Blunos of the same model can automatically connect to each other when turned on and don't need any manual setup. 
<br/>

## Perception Test
1) Setup the arduinos
2) `DirectionPerception/directionPerception.py` automatically generate a set of angles that the belts viberate at. Change the variable 'numMotors' to fit the number of motor you have in the belt. `DirectionPerception/directionPerceptionImpulse.py` and `DirectionPerception/directionPerceptionGaussian.py` runs impulse and Gaussian tests respectively. There are three schemas of Gaussian test that you can choose fro: 1 motor, 3 motors, and 5 motors.<br/>
3) `DirectionPerception/directionPerception.py` will generate a .txt file that records the actual viberating angle and the perceived angle, named `DirPer_#mtr_sub#.txt`. The first line of `DirPer_#mtr_sub#.txt`contains subject angle response, the second line contains the actual vibration angle and vibration scheme. Data is seperated by comma.
4) `DirectionPerception/dirPerAnalyze.py` then take `DirPer_8mtr_sub#.txt`, `DirPer_12mtr_sub#.txt`, and `DirPer_16mtr_sub#.txt` file to analyze and plot the average directional error across different experimental conditions (belt types and vibration schemes) for a given subject. There should be 3 plots generated from running this code.

## Open Loop (Discrete Control Navigation)
In this experiment, participants navigated through seven waypoints using only belt cues, with movement controlled via W-A-S-D keys. 


## Closed Loop (Continuous Feedback Navigation)
This experiment evaluated continuous feedback navigation using haptic belts, where vibrational cues were updated every 0.4 seconds based on the user's position.

## Materials
- ``EverythingOld``: Julian's and Viktor's thesis. Julian's thesis presentation slides and Jame's project review slides. Also some code used for testing. <br />
- (Others are to be updated)

## Ackowledgement
Many thanks to James Falandays for sharing the code in 2022. 
