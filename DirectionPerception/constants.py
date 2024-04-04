class constants:
    # Stores the constants for all haptic belt tests

    ######################################################################################################################
    # General constants for communication with Arduino

    MSG_START = 255  # Represents the start of a data stream - needs to match arduino code, must be >0, <26
    MSG_END = 254  # Represents the end of a data stream - needs to match arduino code, must be >0, <26
    SERIAL_BAUDRATE = 115200  # The baudrate for serial
    REFRESH_RATE = 1 / 90.0  # Refresh rate for Vizard timer, used when looping main function
    BUFFER_RESET_TIME = 5.0  # Interval at which the buffers are reset



    ######################################################################################################################
    # Relative Intensity Constants

    #Relative intensity constants
    LEFT_MOTOR = 1                  #Motor ID for left motor in 12 motor belt
    RIGHT_MOTOR = LEFT_MOTOR + 1    #Motor ID for right motor in 12 motor belt

    # This stores the different intensity bins. The first number in each triplet is the number of trials in that bin
    # The second is the lower bound of the bin. The third is the upper bound of that bin
    WARMUP_INTENSITIES = [(240,5),(40,200),(120,130),(0,40),(180,95),(1,1),(200,140),(30,70),(150,170),(255,255)]
    BINS = [(3, 193, 255), (3, 129, 192), (3, 78, 128), (3, 52, 77), (2, 39, 51),(2,27,38), (2, 14, 26), (2, 1, 13), (2, 0, 0)]  #Intensity bins
    REPS = 5                #Number of repetitions we want for each bin
    MAX_TRIAL_DURATION = 5  #The maximum time the subject has to respond to a cue

    #Codes for each condition
    SAME = 0; LEFT = 1; RIGHT = 2; NEITHER = 3

    #Display variables
    DISPLAY_SIZE = (1100, 750)  # Size of pygame display (width, height)
    BACKGROUND_COLOR = (0,0,0)
    TEXT_COLORS = [(0, 255, 0), (0, 0, 255), (255, 0, 0)]
    INSTRUCTIONS_COLOR = (255,255,255)
    LABEL_SEPARATION = 40
    START_TEXT = "Press space to start"
    INSTRUCTIONS = ["'A' - left stronger", "'D' - right stronger", "'S' - both equal", "'W' - no vibration"]

    ######################################################################################################################
    # Direction Constants
    #WARMUP_ANGLES = [(0,0),(180,0),(90,0),(270,0),('OFF',0),(37,1),(201,1),(333,1),(103,1),('STOP',1)]
    WARMUP_ANGLES_IMPULSE = [(0,0),(180,0),(90,0),(270,0),('OFF',0)]
    MAX_MOTORS = 16    #Used to define the number of total colocated cues
    NUM_BINS = 20      #Number of bins for the uniform, random cues
    NUM_REPS = 2      #Number of repetitions per cue

    #Define display colors and sizes
    BACKGROUND_COLOR_DIR = (255,255,255)
    CIRCLE_COLOR = (10,10,10)
    CIRCLE_SHIFT = 50
    OUTER_RAD = 330
    INNER_RAD = 310
    ANGLE_LABEL_GAP = 20
    RECT_WIDTH = 166
    RECT_HEIGHT = 100
    RECT_SHIFT = 3*RECT_HEIGHT/4

    #Define text displayed on the screen
    OFF_TEXT = 'OFF signal'
    STOP_TEXT = 'STOP signal'
    INSTRUCT_TEXT = 'Click on the circle or on the relevant button'

    MAX_TRIAL_DURATION_DIR = 7      #Maximum time that each trial lasts
    MIN_CLICK_DELAY = 0             #Time that code waits to save data between consecutive clicks. Helps prevent accidental multi-clicks



    ######################################################################################################################
    #Locomotion constants
    REPS_PER_COND = 2  # Number of repetitions for each of the 2 variable combinations (single-motor or Gaussian)
    REPS_PER_COND_WUP = 2  # Number of repetitions for each of the 2 variable combinations
    NUM_CTRL_PATHS = 2    
    NUM_VAR_COMBS = 2 #Number of variable combinations (2 since we just have Gaussian and single-motor vibrations)
    
    WAYPOINT_RADIUS = 0.3  # If subject is within radius (m), it counts as them having reached the waypoint
    GAUSSIAN_SD = 25  # Standard deviation of Gaussian. Shouldn't be more than 60
    GAUSSIAN_CUTOFF = 0.01  # Intensity cut off for Gaussian. Intensities below this fraction are treated as 0.
    # CANNOT BE 0! Has to allow MSG_START and MSG_END signals to be unique

    WRITE_PERIOD = 0.05  # Reciprocal of the frequency at which the belt gets new data.
    # With the software PWM library, all belts work at this rate. With the other arduino
    # code (without the library), this has to be 0.2s at least.

    STOP_TIME = 1.0  # Time that the stop signal lasts when a waypoint is reached
    CONTROL_PERIOD = 5.0  # Total period for discrete control
    DISCRETE_ON_TIME = 1.0  # Time the signal is active during controlPeriod for discrete control

    RECORD_TIME = 1 / 90.0  # Interval at which position and orientation data is recorded

    REORIENT_PERIOD = 2  # Time subject has to stay at poleToGoTo during reorientation before new trial starts
    REORIENT_RADIUS = 0.5  # Margin of error allowed for reorientation at poleToGoTo

    REORIENT_YAW_ERROR = 40  # Margin of error allowed in yaw for reorientation while facing poleToFace
    REORIENT_PITCH_ERROR = 30  # Margin of error allowed in pitch for reorientation while facing poleToFace
    REORIENT_ROLL_ERROR = 10  # Margin of error allowed in roll for reorientation while facing poleToFace

    # Variables for the reorientation poles (TGT - 'to go to', TF - 'to face'
    POLE_TGT_HEIGHT = 1.0
    POLE_TGT_RADIUS = 0.3
    POLE_TGT_POS = [0, 0, 0]  # DO NOT CHANGE

    POLE_TF_HEIGHT = 4
    POLE_TF_RADIUS = 0.2
    POLE_TF_POS = [0, 0, 45]  # DO NOT CHANGE X,Y (can change Z)

    # Room dimensions for path generation
    ROOM_X = 10
    ROOM_Z = 10

    MIN_WPT_SEP = 3  # Minimum waypoint separation
    MAX_LEN = 6  # Maximum distance between final two waypoints
    
    # Click rate stuff
    CLICK_ON_PERIOD = 0.5
    CLICK_ON_TIME = 0.3
    

    ######################################################################################################################

