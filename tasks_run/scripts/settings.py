import os
import warnings
""" =================================================================="""
""" ====================== ALL SCRIPT MATERIALS ======================"""
""" =================================================================="""
# PATHS
DOCKER_PATH_TO_SETTINGS: str = "/workdir/tasks_run/scripts/settings.py"
TMP_OUTDIR_PATH: str = "/workdir/tasks_run/tmp_outdir"
SAMBASHARE_DIR_PATH: str = "/workdir/tasks_run/data/sambashare"
DATA_DIR_PATH: str = "/workdir/tasks_run/data"
FIXATION_PATH: str = "/workdir/tasks_run/rifg_materials/fixationcross.png"

# USER MESSAGES
INTER_TRIAL_MESSAGE: list = ["", "Please wait for next steps ...", ""]
ENDING_MESSAGE: str = "You have now completed the task. Thank you for participating!"

# EXPERIMENTAL AND MRI PARAMETERS
repetitionTime: float = 1.06
RETRIES_BEFORE_ENDING: int = 3
RETRY_WAIT_TIME: float = 0.25
TRIES_BEFORE_NEW_DCM: int = 2
REST_DURATION: int = 30

# PROJECTION PARAMETERS
SECOND_MONITOR_WIDTH: int = 1920
SECOND_MONITOR_HEIGHT: int = 1080
MONITOR_X_OFFSET: int = 1920  # Position the second monitor to the right of the first monitor
MONITOR_Y_OFFSET: int = 0

FIXATION_WIDTH: int = 200
FIXATION_HEIGHT: int = 200
FIX_LOCATION_SECMON_WIDTH_DIVISOR: float = 2.0
FIX_LOCATION_SECMON_HEIGHT_DIVISOR: float = 2.0
FIX_LOCATION_WIDTH_DIVISOR: float = 2
FIX_LOCATION_HEIGHT_DIVISOR: float = 2
FIX_RECT_REST_DIVISORS: tuple = (2, 2)

FONT_COLOR: tuple = (255, 255, 255)

""" ==================================================================="""
""" ==================================================================="""

""" =========================================================="""
""" ====================== E3 MATERIALS ======================"""
""" =========================================================="""

# ENV VARIABLE SETUP
ENV_CHID=os.getenv('CHID')
E3_HOSTNAME="e3-login.tch.harvard.edu"

if ENV_CHID is None:
    warnings.warn("Environment variable CHID is not set. As a result, some tasks will not work.", UserWarning)
    LOCAL_PATH_TO_PRIVATE_KEY = None
    LOCAL_PATH_TO_PUBLIC_KEY = None
    LOCAL_PATH_TO_SSH_CONFIG_FILE = None
    LOCAL_PATH_TO_KNOWN_HOSTS_FILE = None
else:
    LOCAL_PATH_TO_PRIVATE_KEY: str = f"/workdir/.ssh/docker_e3_key_{ENV_CHID}"
    LOCAL_PATH_TO_PUBLIC_KEY: str = f"/workdir/.ssh/docker_e3_key_{ENV_CHID}.pub"
    LOCAL_PATH_TO_SSH_CONFIG_FILE: str = f"/workdir/.ssh/config_{ENV_CHID}"
    LOCAL_PATH_TO_KNOWN_HOSTS_FILE: str =f"/workdir/.ssh/known_hosts_{ENV_CHID}"

# PATHS
E3_PROJECT_PATH: str = "/lab-share/Neuro-Cohen-e2/Public/projects/ADHD_NFB"
E3_PATH_TO_INPUT_FUNC_DATA: str = os.path.join(E3_PROJECT_PATH, "localizer_data/e3_registration_script/input_data/")
E3_PATH_TO_COMPUTE_EASYREG_SCRIPT: str = os.path.join(E3_PROJECT_PATH, "/localizer_data/store_ip_and_compute_srun.sh")
E3_PATH_TO_IP_LOG: str = os.path.join(E3_PROJECT_PATH, "/localizer_data/ip_list.txt")
E3_PATH_TO_MNI_ACC: str = os.path.join(E3_PROJECT_PATH, "localizer_data/mni_acc_mask.nii.gz")
E3_PATH_TO_MNI_RIFG: str = os.path.join(E3_PROJECT_PATH, "localizer_data/mni_rIFG_mask.nii.gz")
E3_PATH_TO_MNI_MOTOR: str = os.path.join(E3_PROJECT_PATH, "localizer_data/mni_motor_mask.nii.gz")
E3_PATH_TO_MNI_BRAIN: str = os.path.join(E3_PROJECT_PATH, "localizer_data/mni_brain.nii.gz")
E3_PATH_TO_SEGMENTED_BRAIN: str = os.path.join(E3_PROJECT_PATH, "localizer_data/synthseg_mni_brain.nii.gz")
E3_PATH_TO_SETTINGS: str = os.path.join(E3_PROJECT_PATH, "settings.py")
""" ==================================================================="""
""" ==================================================================="""

""" ===================================================================="""
""" ====================== REGISTRATION MATERIALS ======================"""
""" ===================================================================="""
# PATHS
LOCALIZER_FILE_NAME: str = "Localizer.py"
LOCALIZER_LOG_DIR: str = "/workdir/tasks_run/data/localizer_data/logs"
MNI_BRAIN_PATH: str = "/workdir/tasks_run/data/localizer_data/mni_brain.nii.gz"
MNI_ACC_MASK_PATH: str = "/workdir/tasks_run/data/localizer_data/mni_acc_mask.nii.gz"
MNI_MOTOR_MASK_PATH: str = "/workdir/tasks_run/data/localizer_data/mni_motor_mask.nii.gz"
MNI_RIFG_MASK_PATH: str = "/workdir/tasks_run/data/localizer_data/mni_rIFG_mask.nii.gz"
ROI_MASK_DIR_PATH: str = "/workdir/tasks_run/data/localizer_data/subj_space_masks/"
MSIT_EVENT_CSV: str = "/workdir/tasks_run/msit_materials/msit_events.csv"
RIFG_EVENT_CSV: str = "/workdir/tasks_run/rifg_materials/rifg_events_with_rest.csv"
""" ==================================================================="""
""" ==================================================================="""


""" ==================================================================="""
""" ====================== RIFG SCRIPT MATERIALS ======================"""
""" ==================================================================="""
RIFG_SCRIPT_NAME: str = "rifg_task.py"

# PATHS
RIFG_LOG_DIR: str = "/workdir/tasks_run/data/rifg_logs"
BUZZ_PATH: str = "/workdir/tasks_run/rifg_materials/buzz2.png"
BEAR_PATH: str = "/workdir/tasks_run/rifg_materials/mad_lotso.png"
PRESSED_A_PATH: str = "/workdir/tasks_run/rifg_materials/pressed_a.png"

# USER MESSAGES
RIFG_INSTRUCTIONS: list = [
    "Welcome to the Task!",
    "Press 'A' using your left thumb when you see Buzz (the astronaut).",
    "Do NOT press anything when you see Lotso (the pink bear).",
    "When the Fixation Cross (+) appears, please look directly at it.",
    "This task will start and end with 30s of rest.",
    "During rest, you will only see the fixation cross.",
    "Please wait for experimenter to start the experiment..."]

# EXPERIMENTAL AND MRI PARAMETERS
RIFG_N_TRIALS: int = 192
ISI_MIN: int = 250  # in ms
ISI_MAX: int = 1250  # in ms
ISI_STEP: int = 250  # in ms
RANDOM_SEED_VALUE: int = 42

# PROJECTION PARAMETERS
BUZZ_WIDTH_DIVISOR: int = 6  # divisor used to determine the size of new_width_buzz relative to the width of the second monitor.
BUZZ_HEIGHT_DIVISOR: int = 3
BEAR_WIDTH_DIVISOR: int = 6
BEAR_HEIGHT_DIVISOR: int = 3

BUZZ_BEAR_LOCATION_SECMON_WIDTH_DIVISOR: float = 2
BUZZ_BEAR_LOCATION_SECMON_HEIGHT_DIVISOR: float = 2
BUZZ_BEAR_LOCATION_WIDTH_DIVISOR: float = 2
BUZZ_BEAR_LOCATION_HEIGHT_DIVISOR: float = 2

KEYPRESS_WIDTH: int = 600
KEYPRESS_HEIGHT: int = 400
KEYPRESS_LOCATION_SECMON_WIDTH_DIVISOR: float = 1.9
KEYPRESS_LOCATION_SECMON_HEIGHT_DIVISOR: float = 3.3
KEYPRESS_LOCATION_WIDTH_DIVISOR: float = 2
KEYPRESS_LOCATION_HEIGHT_DIVISOR: float = 2

INSTRUCT_TEXT_RECT_SECMON_WIDTH_DIVISOR: int = 2
INSTRUCT_TEXT_RECT_SECMON_HEIGHT_DIVISOR: int = 4

DISPLAY_EXIT_MESSAGE_TIME: int = 5
EXIT_MESSAGE_FONT_SIZE: int = 55

INSTRUCT_MESSAGE_FONT_SIZE: int = 48
INSTRUCT_Y_OFFSET: int = 100
INSTRUCT_Y_OFFSET_INCREMENT: int = 60

""" ==================================================================="""
""" ==================================================================="""



""" ============================================================================"""
""" ====================== NEUROFEEDBACK SCRIPT MATERIALS ======================"""
""" ============================================================================"""
NFB_SCRIPT_NAME: str = "nf_calc_MW.py"

# PATHS
NFB_LOG_DIR: str = "/workdir/tasks_run/data/nfb_logs"
FONT_PATH: str = "/workdir/tasks_run/nfb_materials/Space_Grotesk/SpaceGrotesk-VariableFont_wght.ttf"
BACKGROUND_PATH_1: str = "/workdir/tasks_run/nfb_materials/background_1.png"
BACKGROUND_PATH_2: str = "/workdir/tasks_run/nfb_materials/background_2.png"
BACKGROUND_PATH_3: str = "/workdir/tasks_run/nfb_materials/background_3.png"
BACKGROUND_PATH_4: str = "/workdir/tasks_run/nfb_materials/background_4.png"
ROCKET_PATH: str = "/workdir/tasks_run/nfb_materials/rocket.png"
ROCKET_WITH_FLAMES_PATH: str = "/workdir/tasks_run/nfb_materials/RocketWithFlames.png"
PORTAL_PATH: str = "/workdir/tasks_run/nfb_materials/portal.png"
PRINT_BACKGROUND: str = "/workdir/tasks_run/nfb_materials/scifi_term.png"
COLLISION_WORD_ART: str = "/workdir/tasks_run/nfb_materials/CollisionWordArt.png"
HIGH_PERFORM_WORD_ART: str = "/workdir/tasks_run/nfb_materials/highPerfText.png"

# USER MESSAGES
NFB_INSTRUCTIONS: list = ["Welcome to the Task!", "Please try to make the rocket go into the portal"]
BLOCK_START_MESSAGE: list = ["", "Starting new block...", ""]

# EXPERIMENTAL AND MRI PARAMETERS
NFB_FROM_MEAN_ACTIVATION: bool = True  # Choose one type of NFB, make the other false
NFB_FROM_RESIDUAL_VALUE: bool = False
NFB_N_TRIALS_ODD_BLOCK: int = 140
NFB_N_TRIALS_EVEN_BLOCK: int = 160
STARTING_BLOCK_NUM: int = 1
TRIAL_WINDOW_SIZE: int = 24
START_REST_TRIAL: int = 1
START_NF_TRIAL: int = 3
EVEN_BLOCK_START_2ND_REST: int = 141
TRIALS_BEFORE_STREAK_REPORT: int = 3

# PROJECTION PARAMETERS
ROCKET_WIDTH: int = 250
ROCKET_HEIGHT: int = 250
ROCKET_FLAMES_WIDTH: float = ROCKET_WIDTH * 1.3208  # I calculated that the flames make the ball 32.08% longer, so allocate 32.08% more pixels on the width dimension
ROCKET_FLAMES_HEIGHT: int = 250
INITIAL_ROCKET_LOCATION_SECMON_WIDTH_DIVISOR: float = 2
INITIAL_ROCKET_LOCATION_SECMON_HEIGHT_DIVISOR: float = 2
ROCKET_WIDTH_LOCATION_DIVISOR: float = 2
ROCKET_HEIGHT_LOCATION_DIVISOR: float = 2

COLLISION_WIDTH: int = 400
COLLISION_HEIGHT: int = 150
COLLISION_DIVISORS: list = [2.2, 2, 2, 2]
LEVEL_TWO_COLLISION_REQUIREMENTS: int = 5  # collisions before reaching the said level
LEVEL_THREE_COLLISION_REQUIREMENTS: int = 10  # collisions before reaching the said level
LEVEL_FOUR_COLLISION_REQUIREMENTS: int = 20  # collisions before reaching the said level
LEVEL_TWO_COLLISION_ADJUSTMENT_X: int = 25
LEVEL_TWO_COLLISION_ADJUSTMENT_Y: int = 25
LEVEL_THREE_COLLISION_ADJUSTMENT_X: int = 55
LEVEL_THREE_COLLISION_ADJUSTMENT_Y: int = 45
LEVEL_FOUR_COLLISION_ADJUSTMENT_X: int = 90
LEVEL_FOUR_COLLISION_ADJUSTMENT_Y: int = 75

STREAK_WIDTH: int = 600
STREAK_HEIGHT: int = 400
STREAK_LOCATION_DIVISORS: tuple = (2.2, 2, 2.5, 2)

PORTAL_WIDTH: int = 500
PORTAL_HEIGHT: int = 600
PORTAL_LOCATION_SECMON_WIDTH_DIVISOR: float = 1.2
PORTAL_LOCATION_SECMON_HEIGHT_DIVISOR: float = 2
PORTAL_WIDTH_LOCATION_DIVISOR: float = 2
PORTAL_HEIGHT_LOCATION_DIVISOR: float = 2

PRINT_BG_LOCATION_DIVISORS: list = [2, 2, 5.25, 5]
PRINT_LEVEL_LOCATION_DIVISORS: list = [2, 2, 5, 5.5]

""" ==================================================================="""
""" ==================================================================="""



""" ==================================================================="""
""" ====================== MSIT SCRIPT MATERIALS ======================"""
""" ==================================================================="""
MSIT_SCRIPT_NAME_PRE: str = "MSIT_NF_PRE.py"
MSIT_SCRIPT_NAME_POST: str = "MSIT_NF_POST.py"

# PATHS
MSIT_LOG_DIR: str = "/workdir/tasks_run/data/msit_logs"

# USER MESSAGES
MSIT_INSTRUCTIONS = [
    "Welcome to the MSIT Task! ",
    "Please indicate which number is different from the numbers shown on the screen.",
    "If it's 1, press A using your left index finger. ",
    "If it's 2, press B using your left thumb.",
    "If it's 3, press C using your right index finger.",
    "If you miss one, don't worry, just keep going!",
    "When the Fixation Cross (+) appears, please look directly at it."
]

# EXPERIMENTAL AND MRI PARAMETERS
MSIT_N_TRIALS: int = 192
MSIT_TIME_TO_SHOW_FEEDBACK: float = 0.5

# PROJECTION PARAMETERS
MSIT_FONT_SIZE_NUMBERS: int = 200
MSIT_FONT_SIZE_FEEDBACK: int = 75
MSIT_SCREEN_DIVISORS_FOR_NUMBERS: tuple = (2, 2)
MSIT_SCREEN_DIVISORS_FOR_FEEDBACK: tuple = (2, 4)

#MSIT VARIABLES
CONTROL_BLOCK = 333
INTERFERENCE_BLOCK = 444
TRIALS_PER_SESSION = 24
NUM_SESSIONS = 8
ISI = 1.75  # seconds
CONTROL_SEEDS_PRE = [42, 88, 3, 78]
INTERFERENCE_SEEDS_PRE = [55, 99, 50, 18]
CONTROL_SEEDS_POST = [24, 66, 8, 87]
INTERFERENCE_SEEDS_POST = [44, 92, 33, 71]

""" ==================================================================="""
""" ==================================================================="""
