import os
import warnings
import sys

"""
Variables assigned here are used in the task scripts. 
The aims for most paths to be relative to this directory so they may be used across computers and both inside and outside docekr containers.
The script will also check for the existance of all (non-e3) paths upon it being called by other scripts. 
If a path is not found, the script will raise a warning to the user
"""

def check_for_paths(this_script_path: str, verbose: bool) -> list: 
    global_vars = globals().copy()

    # Check for "Neuro-Cohen-e2" in the script path to enable E3 path checks
    check_E3_paths = "Neuro-Cohen-e2" in this_script_path
    if check_E3_paths and verbose:
        print("Checking for existence of E3 settings paths.")
    elif not check_E3_paths and verbose:
        print("Checking local scripts now ...")
    
    nonexistant_vars: list = []
    for var_name, path_var in global_vars.items():
        if isinstance(path_var, str) and ("\\" in path_var or "/" in path_var):
            if var_name == "TZ":
                continue
            # Normalize the path
            normalized_path = os.path.normpath(path_var)

            # Check if the path is empty first
            if not path_var or path_var == "":
                warnings.warn(f"Path for settings variable {var_name} is empty. Check {var_name} at: {this_script_path}")
                nonexistant_vars.append(var_name)

            # Separate E3 path handling
            if check_E3_paths and "E3" in var_name:
                if verbose:
                    print(f"Checking {var_name}: {path_var} ... ")

                if not os.path.exists(normalized_path):
                    warnings.warn(f"Cannot find path for E3 settings variable {var_name}: {path_var}. Check {var_name} at: {this_script_path}")
                    nonexistant_vars.append(var_name)

                elif verbose:
                    print("Path found sucessfully.")

            elif not check_E3_paths and "E3" not in var_name:
                if verbose:
                    print(f"Checking {var_name}: {path_var} ... ")

                if not os.path.exists(normalized_path):
                    warnings.warn(f"Cannot find path for settings variable {var_name}: {path_var}. Check {var_name} at: {this_script_path}")
                    nonexistant_vars.append(var_name)

                elif verbose:
                    print("Path found sucessfully.")
    
    print(f"\nNumber of non-existant paths: {len(nonexistant_vars)}\n")

    return nonexistant_vars

def make_env_vars(env_var_script_path: str, nonexistant_vars: list, verbose: bool):
    vars_to_make = {}
    if verbose:
        print("Writing environment variables to env script... ")
    

    if os.path.exists(env_var_script_path):
        if verbose:
            print("Removing old env script ...")
            os.remove(env_var_script_path)

    for arg in sys.argv[1:]:
        if not arg in globals().copy():
            print(f"The inputted arg: '{arg}' is not a variable in this script ")
        elif arg in nonexistant_vars:
            print(f"The inputted arg: '{arg}' has a nonexistant path. Skipping this variable ...")
        else:
            if verbose:
                print(f"Adding env var: '{arg}'")

            vars_to_make[arg] = globals()[arg]

    if verbose:
        print(f"Sending to env script path at: {env_var_script_path}")
    with open(env_var_script_path, "w") as f:
        for key, item in vars_to_make.items():
            if verbose:
                print(f"adding environment var: {key} with value: {item}")
            
            f.write(f'export {key}="{item}"\n')    

"""
========================
 USER VARIABLES
========================
"""
USER=os.getenv('USER')
ENV_CHID = os.getenv('CHID')
            
"""
========================
 MAIN DIRECTORY PATHS
========================
"""
SETTINGS_PATH = os.path.abspath(__file__)
SCRIPT_DIRECTORY_PATH = os.path.dirname(SETTINGS_PATH)
TASKS_RUN_PATH = os.path.dirname(SCRIPT_DIRECTORY_PATH)
DATA_DIR_PATH = os.path.join(TASKS_RUN_PATH, "data")
PROJECT_DIRECTORY = os.path.dirname(TASKS_RUN_PATH)
LOCAL_SAMBASHARE_DIR_PATH = "/Users/samba_user/sambashare"
SAMBASHARE_DIR_PATH = os.path.join(DATA_DIR_PATH, "sambashare")
DOCKER_RUN_PATH = os.path.join(PROJECT_DIRECTORY, "docker_run")
TMP_OUTDIR_PATH = os.path.join(TASKS_RUN_PATH, "tmp_outdir")

BULL_PATH = "/bull/path"

"""
================================
 ACROSS-TASK VARIABLES / KNOBS
================================
"""
# USER MESSAGES
INTER_TRIAL_MESSAGE: list = ["", "Please wait for next steps ...", ""]
ENDING_MESSAGE: str = "You have now completed the task. Thank you for participating!"

# EXPERIMENTAL AND MRI PARAMETERS
repetitionTime: float = 1.06
RETRIES_BEFORE_ENDING: int = 3
RETRY_WAIT_TIME: float = 0.25
TRIES_BEFORE_NEW_DCM: int = 2
REST_DURATION: int = 5
RANDOM_SEED_VALUE: int = 42

# PROJECTION PARAMETERS
SECOND_MONITOR_WIDTH: int = 1920
SECOND_MONITOR_HEIGHT: int = 1080
MONITOR_X_OFFSET: int = 1470  # Position the second monitor to the right of the first monitor
MONITOR_Y_OFFSET: int = -100

FIXATION_WIDTH: int = 200
FIXATION_HEIGHT: int = 200
FIX_LOCATION_SECMON_WIDTH_DIVISOR: float = 2.0
FIX_LOCATION_SECMON_HEIGHT_DIVISOR: float = 2.0
FIX_LOCATION_WIDTH_DIVISOR: float = 2
FIX_LOCATION_HEIGHT_DIVISOR: float = 2
FIX_RECT_REST_DIVISORS: tuple = (2, 2)

FONT_COLOR: tuple = (255, 255, 255)

ENV_VAR_SCRIPT = os.path.join(TMP_OUTDIR_PATH, "env_vars.sh")

TZ="America/New_York"

"""
========================
 E3 AND SSH MATERIALS
========================
"""

E3_HOSTNAME = "e3-login.tch.harvard.edu"
SSH_DIRECTORY = os.path.join(PROJECT_DIRECTORY, ".ssh")

# E3 PATHS
E3_PROJECT_PATH = "/lab-share/Neuro-Cohen-e2/Public/projects/ADHD_NFB"
E3_PATH_TO_SETTINGS = os.path.join(E3_PROJECT_PATH, "settings.py")
E3_LOCALIZER_DIR = os.path.join(E3_PROJECT_PATH, "localizer_data")
E3_PATH_TO_RIFG_LOGS = os.path.join(E3_PROJECT_PATH, "rifg_logs")
E3_PATH_TO_SAMBASHARE = os.path.join(E3_PROJECT_PATH, "sambashare")
E3_PATH_TO_NFB_LOGS = os.path.join(E3_PROJECT_PATH, "nfb_logs")
E3_PATH_TO_MSIT_LOGS = os.path.join(E3_PROJECT_PATH, "msit_logs")

E3_PATH_TO_MNI_ACC = os.path.join(E3_LOCALIZER_DIR, "mni_acc_mask.nii.gz")
E3_PATH_TO_MNI_RIFG = os.path.join(E3_LOCALIZER_DIR, "mni_rIFG_mask.nii.gz")
E3_PATH_TO_MNI_MOTOR = os.path.join(E3_LOCALIZER_DIR, "mni_motor_mask.nii.gz")
E3_PATH_TO_MNI_BRAIN = os.path.join(E3_LOCALIZER_DIR, "mni_brain.nii.gz")
E3_PATH_TO_SEGMENTED_BRAIN = os.path.join(E3_LOCALIZER_DIR, "synthseg_mni_brain.nii.gz")
E3_PATH_TO_IP_LOG = os.path.join(E3_LOCALIZER_DIR, "ip_list.txt")
E3_REGISTRATION_DIR = os.path.join(E3_LOCALIZER_DIR, "e3_registration_script")
E3_PATH_TO_LOCALIZER_DATA_LOGS = os.path.join(E3_LOCALIZER_DIR, "logs")
E3_PATH_TO_SUBJECT_SPACE_MASKS = os.path.join(E3_LOCALIZER_DIR, "subj_space_masks")

E3_PATH_TO_INPUT_FUNC_DATA = os.path.join(E3_REGISTRATION_DIR, "input_data")
E3_PATH_TO_TEMP_DIR = os.path.join(E3_REGISTRATION_DIR, "tmp_outdir")
E3_PATH_TO_OUTPUT_MASK = os.path.join(E3_REGISTRATION_DIR, "output_data")

if ENV_CHID is None:
    warnings.warn("Environment variable CHID is not set.", UserWarning)
    LOCAL_PATH_TO_PRIVATE_KEY = None
    LOCAL_PATH_TO_PUBLIC_KEY = None
    LOCAL_PATH_TO_SSH_CONFIG_FILE = None
    LOCAL_PATH_TO_KNOWN_HOSTS_FILE = None
else:
    LOCAL_PATH_TO_PRIVATE_KEY = os.path.join(SSH_DIRECTORY, f"docker_e3_key_{ENV_CHID}")
    LOCAL_PATH_TO_PUBLIC_KEY = os.path.join(SSH_DIRECTORY, f"docker_e3_key_{ENV_CHID}.pub")
    LOCAL_PATH_TO_SSH_CONFIG_FILE = os.path.join(SSH_DIRECTORY, f"config_{ENV_CHID}")
    LOCAL_PATH_TO_KNOWN_HOSTS_FILE = os.path.join(SSH_DIRECTORY, f"known_hosts_{ENV_CHID}")

"""
========================
 LOCALIZER MATERIALS
========================
"""

LOCALIZER_FILE_NAME = "2_Realtime_Localizer.py"
LOCALIZER_DIR = os.path.join(DATA_DIR_PATH, "localizer_data")
LOCALIZER_LOG_DIR = os.path.join(LOCALIZER_DIR, "logs")
MNI_BRAIN_PATH = os.path.join(LOCALIZER_DIR, "mni_brain.nii.gz")
MNI_ACC_MASK_PATH = os.path.join(LOCALIZER_DIR, "mni_acc_mask.nii.gz")
MNI_MOTOR_MASK_PATH = os.path.join(LOCALIZER_DIR, "mni_motor_mask.nii.gz")
MNI_RIFG_MASK_PATH = os.path.join(LOCALIZER_DIR, "mni_rIFG_mask.nii.gz")
ROI_MASK_DIR_PATH = os.path.join(LOCALIZER_DIR, "subj_space_masks")
MSIT_MATERIAL_DIR = os.path.join(TASKS_RUN_PATH, "msit_materials")
RIFG_MATERIAL_DIR = os.path.join(TASKS_RUN_PATH, "rifg_materials")
MSIT_EVENT_CSV = os.path.join(MSIT_MATERIAL_DIR, "msit_events.csv")
RIFG_EVENT_CSV = os.path.join(RIFG_MATERIAL_DIR, "rifg_event_with_rest_predeterminedISI.csv")

"""
========================
 RIFG MATERIALS
========================
"""
RIFG_SCRIPT_NAME = "1_Task_RIFG.py"

# PATHS
RIFG_LOG_DIR = os.path.join(DATA_DIR_PATH, "rifg_logs")
BUZZ_PATH = os.path.join(RIFG_MATERIAL_DIR, "buzz2.png")
BEAR_PATH = os.path.join(RIFG_MATERIAL_DIR, "mad_lotso.png")
PRESSED_A_PATH = os.path.join(RIFG_MATERIAL_DIR, "pressed_a.png")


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
PREDETERMINED_ISI = 1000 # in ms

RIFG_PRE_SEED = 12345
RIFG_POST_SEED = 54321

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
KEYPRESS_LOCATION_SECMON_WIDTH_DIVISOR: float = 1.85
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

"""
=========================
 NEUROFEEDBACK MATERIALS
=========================
"""
NFB_SCRIPT_NAME = "1_Task_NFB.py"

# PATHS
NFB_LOG_DIR = os.path.join(DATA_DIR_PATH, "nfb_logs")
NFB_MATERIAL_DIR = os.path.join(TASKS_RUN_PATH, "nfb_materials")
FONT_PATH = os.path.join(NFB_MATERIAL_DIR, "Space_Grotesk/SpaceGrotesk-VariableFont_wght.ttf")
BACKGROUND_PATH_1 = os.path.join(NFB_MATERIAL_DIR, "background_1.png")
BACKGROUND_PATH_2 = os.path.join(NFB_MATERIAL_DIR, "background_2.png")
BACKGROUND_PATH_3 = os.path.join(NFB_MATERIAL_DIR, "background_3.png")
BACKGROUND_PATH_4 = os.path.join(NFB_MATERIAL_DIR, "background_4.png")
ROCKET_PATH = os.path.join(NFB_MATERIAL_DIR, "rocket.png")
ROCKET_WITH_FLAMES_PATH = os.path.join(NFB_MATERIAL_DIR, "RocketWithFlames.png")
PORTAL_PATH = os.path.join(NFB_MATERIAL_DIR, "portal.png")
PRINT_BACKGROUND = os.path.join(NFB_MATERIAL_DIR, "scifi_term.png")
COLLISION_WORD_ART = os.path.join(NFB_MATERIAL_DIR, "CollisionWordArt.png")
HIGH_PERFORM_WORD_ART = os.path.join(NFB_MATERIAL_DIR, "highPerfText.png")

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

"""
=========================
 MSIT MATERIALS
=========================
"""
MSIT_SCRIPT_NAME = "1_Task_MSIT.py"

# PATHS
MSIT_LOG_DIR = os.path.join(DATA_DIR_PATH, "msit_logs")

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
MSIT_TRIALS_PER_BLOCK = 24
MSIT_NUM_BLOCKS = 8
MSIT_ISI = 1.75  # seconds
MSIT_PERCENT_WRONG_BEFORE_WARNING = 0.5
MSIT_PERCENT_SKIPPED_BEFORE_WARNING = 0.5
MSIT_PERCENT_INVALID_BEFORE_WARNING = 0.5

# PROJECTION PARAMETERS
MSIT_FONT_SIZE_NUMBERS: int = 200
MSIT_FONT_SIZE_FEEDBACK: int = 75
MSIT_SCREEN_DIVISORS_FOR_NUMBERS: tuple = (2, 2)
MSIT_SCREEN_DIVISORS_FOR_FEEDBACK: tuple = (2, 2)
FEEDBACK_COORD_OFFSET: int = 150

# MSIT SEED VARIABLES
MSIT_CONTROL_BLOCK = 333
MSIT_INTERFERENCE_BLOCK = 444
CONTROL_SEEDS_PRE = [42, 88, 3, 78]
INTERFERENCE_SEEDS_PRE = [55, 99, 50, 18]
CONTROL_SEEDS_POST = [24, 66, 8, 87]
INTERFERENCE_SEEDS_POST = [44, 92, 33, 71]

"""
=========================
 REST MATERIALS
=========================
"""
REST_SCRIPT_NAME = "1_Task_REST.py"
REST_LOG_DIR = os.path.join(DATA_DIR_PATH, "rest_logs")

REST_TASK_DURATION: int = 300  # 5 min in seconds
REST_INSTRUCTIONS: list = [f"Starting the rest task.",
                           "You will see a fixation cross for the duration of the task.",
                           "Please look directly the fixation cross."
                           f"This task will take approximately {round((REST_TASK_DURATION/60), 2)} minutes",
                           "Please wait for experimenter to start..."]

REST_MESSAGE_AFTER_DONE: list = [f"This task is complete! Please wait for experimenter ..."]

run_verbose = False
if __name__ == "__main__":
    while True:
        ask_verbose = input("Run verbosely? (y/n): ")
        if ask_verbose == 'y':
            run_verbose = True
            break
        elif ask_verbose == 'n':
            run_verbose = False
            break
        else:
            print("Please enter either 'y' or 'n'")
nonexistant_vars = check_for_paths(this_script_path=SETTINGS_PATH, verbose=run_verbose)
if len(sys.argv) > 1:
    make_env_vars(env_var_script_path=ENV_VAR_SCRIPT, 
                  nonexistant_vars=nonexistant_vars,
                  verbose=run_verbose)