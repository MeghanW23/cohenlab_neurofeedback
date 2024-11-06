import os
import warnings
import sys

def run_functions(arguments: list, this_script_path: str, docker_workdir_name, PROJECT_DIRECTORY):
    if len(arguments) > 0 and arguments[0] == "docker":
        if arguments[-1] == "-s":
            check_for_paths(this_script_path=this_script_path, 
                            verbose=False, 
                            suppress=True, 
                            PROJECT_DIRECTORY=PROJECT_DIRECTORY, 
                            docker_workdir_name=docker_workdir_name)
            print_a_path(arguments=arguments[1:-1])
        elif arguments[-1] == "-v":
            check_for_paths(this_script_path=this_script_path, 
                            verbose=True, suppress=False, 
                            PROJECT_DIRECTORY=PROJECT_DIRECTORY, 
                            docker_workdir_name=docker_workdir_name)
            print_a_path(arguments=arguments[1:-1])
        else:
            check_for_paths(this_script_path=this_script_path, 
                            verbose=False, suppress=False, 
                            PROJECT_DIRECTORY=PROJECT_DIRECTORY,
                            docker_workdir_name=docker_workdir_name)
            print_a_path(arguments=arguments[1:])
    else: 
        if len(arguments) > 0 and arguments[-1] == "-s":
            check_for_paths(this_script_path=this_script_path, 
                            verbose=False, 
                            suppress=True, 
                            PROJECT_DIRECTORY=PROJECT_DIRECTORY, 
                            docker_workdir_name=docker_workdir_name)
            print_a_path(arguments=arguments[:-1])
        elif len(arguments) > 0 and arguments[-1] == "-v":
            check_for_paths(this_script_path=this_script_path, 
                            verbose=True, 
                            suppress=False, 
                            PROJECT_DIRECTORY=PROJECT_DIRECTORY,
                            docker_workdir_name=docker_workdir_name)
            print_a_path(arguments=arguments[:-1])
        else:
            check_for_paths(this_script_path=this_script_path, 
                            verbose=False, 
                            suppress=False, 
                            PROJECT_DIRECTORY=PROJECT_DIRECTORY,
                            docker_workdir_name=docker_workdir_name)
            print_a_path(arguments=arguments)

def setup_main_paths(arguments, docker_workdir_name, tasks_dir_name, script_dir_name, settings_script_name):
    if len(arguments) > 0:
        if arguments[0] == "docker":
            PROJECT_DIRECTORY = docker_workdir_name
            TASKS_RUN_PATH = os.path.join(PROJECT_DIRECTORY, tasks_dir_name)
            SCRIPT_DIRECTORY_PATH = os.path.join(TASKS_RUN_PATH, script_dir_name)
            SETTINGS_PATH = os.path.join(SCRIPT_DIRECTORY_PATH, settings_script_name)
            
        else:    
            SETTINGS_PATH = os.path.abspath(__file__)
            SCRIPT_DIRECTORY_PATH = os.path.dirname(SETTINGS_PATH)
            TASKS_RUN_PATH = os.path.dirname(SCRIPT_DIRECTORY_PATH)
            PROJECT_DIRECTORY = os.path.dirname(TASKS_RUN_PATH)

    else:
        SETTINGS_PATH = os.path.abspath(__file__)
        SCRIPT_DIRECTORY_PATH = os.path.dirname(SETTINGS_PATH)
        TASKS_RUN_PATH = os.path.dirname(SCRIPT_DIRECTORY_PATH)
        PROJECT_DIRECTORY = os.path.dirname(TASKS_RUN_PATH)
        
    return PROJECT_DIRECTORY, TASKS_RUN_PATH, SCRIPT_DIRECTORY_PATH, SETTINGS_PATH

def check_for_paths(this_script_path: str, verbose: bool, suppress: bool, PROJECT_DIRECTORY, docker_workdir_name): 
    global_vars = globals().copy()

    # Check for "Neuro-Cohen-e2" in the script path to enable E3 path checks
    check_E3_paths = "Neuro-Cohen-e2" in this_script_path
    if check_E3_paths and verbose:
        print("Checking for existence of E3 settings paths.")
    elif not check_E3_paths and verbose:
        if docker_workdir_name in PROJECT_DIRECTORY:
            print("Checking docker scripts ... ")
        else:
            print("Checking local scripts ...")
    
    nonexistant_vars: list = []
    for var_name, path_var in global_vars.items():
        if isinstance(path_var, str) and ("\\" in path_var or "/" in path_var):
            if var_name == "TZ" or var_name == "DOCKER_WORKDIR_NAME":
                continue
            # Normalize the path
            normalized_path = os.path.normpath(path_var)

            # Check if the path is empty first
            if not path_var or path_var == "":
                if not suppress:
                    warnings.warn(f"Path for settings variable {var_name} is empty. Check {var_name} at: {this_script_path}")
                nonexistant_vars.append(var_name)

            # Separate E3 path handling
            if check_E3_paths and "E3" in var_name:
                if verbose:
                    print(f"Checking {var_name}: {path_var} ... ")

                if not os.path.exists(normalized_path):
                    if not suppress:
                        warnings.warn(f"Cannot find path for E3 settings variable {var_name}: {path_var}. Check {var_name} at: {this_script_path}")
                    nonexistant_vars.append(var_name)

                elif verbose:
                    print("Path found sucessfully.")

            elif not check_E3_paths and "E3" not in var_name:
                if verbose:
                    print(f"Checking {var_name}: {path_var} ... ")

                if PROJECT_DIRECTORY in path_var and not os.path.exists(PROJECT_DIRECTORY):
                    if not suppress:
                        warnings.warn("Settings script cannot check paths (calling script paths from outside the filesystem that the paths exist in)")
                    return []

                if not os.path.exists(normalized_path):
                    if not suppress:
                        warnings.warn(f"Cannot find path for settings variable {var_name}: {path_var}. Check {var_name} at: {this_script_path}")
                    nonexistant_vars.append(var_name)

                elif verbose:
                    print("Path found sucessfully.")
    
    if len(nonexistant_vars) > 0 and not suppress: 
        warnings.warn(f"Number of non-existant paths: {len(nonexistant_vars)}")

def print_a_path(arguments):
    if len(arguments) == 0:
        return None
    elif len(arguments) == 1 and "docker" in arguments:
        return None
    else:
        for argument in arguments:
            if argument == "docker" or argument == "-s" or argument == "-v":
                continue
            elif argument in list(globals().keys()):
                print(globals()[argument])
            else:
                print(f"Could Not find inputted variable {argument} in the settings directory")
        
        return None

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
DOCKER_WORKDIR_NAME = "/workdir"
( PROJECT_DIRECTORY, 
 TASKS_RUN_PATH, 
 SCRIPT_DIRECTORY_PATH, 
 SETTINGS_PATH ) = setup_main_paths(arguments=sys.argv[1:],
                                    docker_workdir_name=DOCKER_WORKDIR_NAME,
                                    tasks_dir_name="tasks_run",
                                    script_dir_name="scripts",
                                    settings_script_name="settings.py")

DATA_DIR_PATH = os.path.join(TASKS_RUN_PATH, "data")
LOCAL_SAMBASHARE_DIR_PATH = "/Users/samba_user/sambashare"
SAMBASHARE_DIR_PATH = os.path.join(DATA_DIR_PATH, "sambashare") # for use inside docker container, etc. 
DOCKER_RUN_PATH = os.path.join(PROJECT_DIRECTORY, "docker_run")
TMP_OUTDIR_PATH = os.path.join(TASKS_RUN_PATH, "tmp_outdir")
DOCKER_PATH_TO_STARTUP_SCRIPT = os.path.join(DOCKER_RUN_PATH, "startup.sh")
USERS_FILE = os.path.join(DOCKER_RUN_PATH, "users.txt")
BULL_PATH="/workdir"

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
REST_DURATION: int = 1
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

TZ="America/New_York"

"""
===========================================
 UTILITY SCRIPT PATHS AND OTHER TEST FILES
===========================================
"""
UTILITY_SCRIPTS_DIR = os.path.join(SCRIPT_DIRECTORY_PATH, "utility_scripts")
TRANSFER_FILES_SCRIPT = os.path.join(UTILITY_SCRIPTS_DIR, "TransferFilesE3.sh")
CLEAR_DIRS_SCRIPT = os.path.join(UTILITY_SCRIPTS_DIR, "ClearDirs.py")
SSH_COMMAND_SCRIPT = os.path.join(UTILITY_SCRIPTS_DIR, "ssh_to_e3.sh")
TEST_PYGAME_SCRIPT = os.path.join(DOCKER_RUN_PATH, "test_pygame.py")
COMPARE_SETTINGS_SCRIPT = os.path.join(UTILITY_SCRIPTS_DIR, "CompareSettingsDifferences.sh")
MAKE_LOCAL_VENV_SCRIPT = os.path.join(DOCKER_RUN_PATH, "make_local_venv.sh")
LOCAL_VENV_DIR_PATH = os.path.join(DOCKER_RUN_PATH, "local_venv")
LOCAL_VENV_REQUIREMENTS_FILE = os.path.join(DOCKER_RUN_PATH, "local_requirements.txt")
TEST_EASYREG_NEW_SCRIPT = os.path.join(SCRIPT_DIRECTORY_PATH, "other/ssh_easyreg_2.sh")
PREDETERMINED_ISI_MAKER_DIR = os.path.join(SCRIPT_DIRECTORY_PATH, "other/Predetermined_ISI")
MAKE_E3_SSH_KEYS = os.path.join(UTILITY_SCRIPTS_DIR, "make_e3_ssh_key.sh")
MAKE_LOCAL_SSH_KEYS = os.path.join(UTILITY_SCRIPTS_DIR, "get_ssh_keys.sh")

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
E3_COMPUTE_PATH=os.path.join(E3_LOCALIZER_DIR, "store_ip_and_compute_srun.sh")
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
E3_PATH_TO_GET_MASK_PATH_SCRIPT = os.path.join(E3_REGISTRATION_DIR, "get_mask_to_pull_from_e3.sh")
E3_RUN_EASYREG_SCRIPT = os.path.join(E3_REGISTRATION_DIR, "run_easyreg.sh")
E3_EASYREG_INITIALIZE_PATH = os.path.join(E3_REGISTRATION_DIR, "easyreg_initialize.sh")
E3_EASYREG_REGISTRATION_SCRIPT = os.path.join(E3_REGISTRATION_DIR, "easyreg_registration.py")
E3_PUSH_MASK_TO_LOCAL = os.path.join(E3_REGISTRATION_DIR, "push_mask_to_docker.sh")

E3_SSH_DIR = os.path.join(E3_PROJECT_PATH, "ssh")
E3_MAKE_SSH_KEYS = os.path.join(E3_PROJECT_PATH, "make_ssh_key.sh")



if ENV_CHID is None:
    if "-s" not in sys.argv:
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


E3_TESTING_LOCALIZER_DIR = os.path.join(E3_PROJECT_PATH, "localizer")
E3_PATH_TO_INPUT_DIRECTORIES = os.path.join(E3_TESTING_LOCALIZER_DIR, "input_dicom_directories")
E3_PATH_TO_WORKING_DIR = os.path.join(E3_TESTING_LOCALIZER_DIR, "localizer_working_dir")
TESTING_LOCALIZER_SSH_COMMAND = os.path.join(SCRIPT_DIRECTORY_PATH, "other/e3_localizer_ssh_comand.sh")
E3_TESTING_LOCALIZER_COMPUTE_PATH = os.path.join(E3_TESTING_LOCALIZER_DIR, "1_store_ip_and_compute_srun.sh")
E3_WAIT_FOR_DATA_SCRIPT = os.path.join(E3_TESTING_LOCALIZER_DIR, "2_wait_for_data.sh")


"""
========================
 LOCALIZER MATERIALS
========================
"""

LOCALIZER_FILE_NAME = "2_Realtime_Localizer.py"
LOCALIZER_SCRIPT = os.path.join(SCRIPT_DIRECTORY_PATH, LOCALIZER_FILE_NAME)

REGISTER_FNIRT_FILE_NAME = "2_Realtime_RegisterFnirt.sh"
REGISTER_FNIRT_SCRIPT = os.path.join(SCRIPT_DIRECTORY_PATH, REGISTER_FNIRT_FILE_NAME)

REGISTER_EASYREG_FILE_NAME = "2_Realtime_PreprocRegisterE3.sh"
REGISTER_EASYREG_SCRIPT = os.path.join(SCRIPT_DIRECTORY_PATH, REGISTER_EASYREG_FILE_NAME)

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
POST_RIFG_EVENT_CSV = os.path.join(RIFG_MATERIAL_DIR, "postRIFG_events.csv")
PRE_RIFG_EVENT_CSV = os.path.join(RIFG_MATERIAL_DIR, "preRIFG_events.csv")


LOCAL_MASK_DIR_PATH = os.getenv('LOCAL_MASK_DIR_PATH')

CLUSTER_THRESHOLD = 10 # Cluster size threshold, in voxels. In the returned thresholded map, sets of connected voxels (clusters) with size smaller than this number will be removed.
TASK_METADATA_TAG = (0x0018, 0x1030)
"""
========================
 RIFG MATERIALS
========================
"""
RIFG_SCRIPT_NAME = "1_Task_RIFG.py"

# PATHS
RIFG_TASK_SCRIPT = os.path.join(SCRIPT_DIRECTORY_PATH, RIFG_SCRIPT_NAME)
RIFG_LOG_DIR = os.path.join(DATA_DIR_PATH, "rifg_logs")
BUZZ_PATH = os.path.join(RIFG_MATERIAL_DIR, "buzz2.png")
BEAR_PATH = os.path.join(RIFG_MATERIAL_DIR, "mad_lotso.png")
PRESSED_A_PATH = os.path.join(RIFG_MATERIAL_DIR, "pressed_a.png")
FIXATION_PATH = os.path.join(RIFG_MATERIAL_DIR, "fixationcross.png")

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
RIFG_N_DICOMS: int = 364
ISI_MIN = 0.25  # in s
ISI_MAX = 1.25  # in s
ISI_STEP = 0.25  # in s
RIFG_TRIAL_DURATION = 0.5 # in s
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
NFB_TASK_SCRIPT = os.path.join(SCRIPT_DIRECTORY_PATH, NFB_SCRIPT_NAME)

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
MSIT_TASK_SCRIPT = os.path.join(SCRIPT_DIRECTORY_PATH, MSIT_SCRIPT_NAME)
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
MSIT_N_DICOMS: int = 364
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
REST_TASK_SCRIPT = os.path.join(SCRIPT_DIRECTORY_PATH, REST_SCRIPT_NAME)
REST_LOG_DIR = os.path.join(DATA_DIR_PATH, "rest_logs")

REST_TASK_DURATION: int = 300  # 5 min in seconds
REST_INSTRUCTIONS: list = [f"Starting the rest task.",
                           "You will see a fixation cross for the duration of the task.",
                           "Please look directly the fixation cross."
                           f"This task will take approximately {round((REST_TASK_DURATION/60), 2)} minutes",
                           "Please wait for experimenter to start..."]

REST_MESSAGE_AFTER_DONE: list = [f"This task is complete! Please wait for experimenter ..."]

if __name__ == "__main__":
    run_functions(arguments=sys.argv[1:], 
                  this_script_path=SETTINGS_PATH, 
                  docker_workdir_name=DOCKER_WORKDIR_NAME,
                  PROJECT_DIRECTORY=PROJECT_DIRECTORY)