'''
The purpose of this script is to analyze data after running vibetest.py
Data from vibetest.py is directly loaded into this script.
'''

# Import statements
import numpy as np
from matplotlib import pyplot as plt
import os

# Loads data [vibeguess, leftStrength, rightStrength]
################################################################################
os.chdir('VibeTests')
vibe_guess = np.load('vibeguess1.npy')
leftStrength = np.load('leftStrength1.npy')
rightStrength = np.load('rightStrength1.npy')

vibe_guess = np.append(np.load('vibeguess2.npy'), vibe_guess)
leftStrength = np.append(np.load('leftStrength2.npy'), leftStrength)
rightStrength = np.append(np.load('rightStrength2.npy'), rightStrength)

vibe_guess = np.append(np.load('vibeguess3.npy'), vibe_guess)
leftStrength = np.append(np.load('leftStrength3.npy'), leftStrength)
rightStrength = np.append(np.load('rightStrength3.npy'), rightStrength)

vibe_guess = np.append(np.load('vibeguess4.npy'), vibe_guess)
leftStrength = np.append(np.load('leftStrength4.npy'), leftStrength)
rightStrength = np.append(np.load('rightStrength4.npy'), rightStrength)

vibe_guess = np.append(np.load('vibeguess5.npy'), vibe_guess)
leftStrength = np.append(np.load('leftStrength5.npy'), leftStrength)
rightStrength = np.append(np.load('rightStrength5.npy'), rightStrength)

vibe_guess = np.append(np.load('vibeguess6.npy'), vibe_guess)
leftStrength = np.append(np.load('leftStrength6.npy'), leftStrength)
rightStrength = np.append(np.load('rightStrength6.npy'), rightStrength)

################################################################################

# Analyzes the data
diff_dict = {}
diff_dict[1] = [] ; diff_dict[2] = [] ; diff_dict[3] = [] ; diff_dict[4] = []
one_dict = {}
one_dict[(1,2)] = [] ; one_dict[(2,1)] = [] ; one_dict[(3,2)] = []
one_dict[(2,3)] = [] ; one_dict[(3,4)] = [] ; one_dict[(4,3)] = []
one_dict[(4,5)] = [] ; one_dict[(5,4)] = []
for (guess, left, right) in zip(vibe_guess, leftStrength, rightStrength):
    diff = abs(left - right)
    if left > right and guess == 0:
        diff_dict[diff].append(1)
    elif right > left and guess == 1:
        diff_dict[diff].append(1)
    else:
        diff_dict[diff].append(0)
    if diff == 1:
        if left > right and guess == 0:
            one_dict[(left, right)].append(1)
        elif right > left and guess == 1:
            one_dict[(left, right)].append(1)
        else:
            one_dict[(left, right)].append(0)
for key in one_dict:
    print("{} mean is {}".format(str(key), str(np.mean(one_dict[key]))))
