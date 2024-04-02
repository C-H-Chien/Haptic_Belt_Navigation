## Introduction
This is a joint research on navigation through Haptic Belt from VEN Lab and LEMS Lab at Brown University, advised under Prof. William Warren and Prof. Benjamin Kimia. The project continues the work done by Julian Volleyson and Viktor Ladics in 2020 and 2021, respectively.

## Perception Test
1) First download the code from `Arduino/blunoMaster` and `Arduino/#_MotorBelt_softPWM` to the arduinos connecting to PC side and belt side respectively.<br/>
2) `DirectionPerception/directionPerception.py` automatically generate a set of angles that the belts viberate at. Change the variable 'numMotors' to fit the number of motor you have in the belt.<br/>
3) `DirectionPerception/directionPerception.py` will generate a .txt file that records the actual viberating angle and the perceived angle, named 'DirPer_#mtr_sub#.txt'.
4) `DirectionPerception/dirPerAnalyze.py` then take 'DirPer_#mtr_sub#.txt' file and generate results.


## Materials
- ``EverythingOld``: Julian's and Viktor's thesis. Julian's thesis presentation slides and Jame's project review slides. Also some code used for testing. <br />
- (Others are to be updated)

## Ackowledgement
Many thanks to James Falandays for sharing the code in 2022. 
