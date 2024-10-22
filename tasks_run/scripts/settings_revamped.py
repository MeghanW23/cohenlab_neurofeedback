import os
import warnings

"""
Variables assigned here are used in the task scripts. 
The aims for most paths to be relative to this directory so they may be used across computers and both inside and outside docekr containers.
The script will also check for the existance of all (non-e3) paths upon it being called by other scripts. 
If a path is not found, the script will raise a warning to the user
"""

def check_for_paths(this_script_path: str): 
    global_vars = globals().copy()

    # Check for "Neuro-Cohen-e2" in the script path to enable E3 path checks
    check_E3_paths = "Neuro-Cohen-e2" in this_script_path
    if check_E3_paths:
        print("Checking for existence of E3 settings paths.")

    for var_name, path_var in global_vars.items():
        if isinstance(path_var, str) and ("\\" in path_var or "/" in path_var):
            # Normalize the path
            normalized_path = os.path.normpath(path_var)

            # Check if the path is empty first
            if not path_var or path_var == "":
                warnings.warn(f"Path for settings variable {var_name} is empty. Check {var_name} at: {this_script_path}")
                continue

            # Separate E3 path handling
            if check_E3_paths and "E3" in var_name:
                if not os.path.exists(normalized_path):
                    warnings.warn(f"Cannot find path for E3 settings variable {var_name}: {path_var}. Check {var_name} at: {this_script_path}")
            elif not check_E3_paths and "E3" not in var_name:
                if not os.path.exists(normalized_path):
                    warnings.warn(f"Cannot find path for settings variable {var_name}: {path_var}. Check {var_name} at: {this_script_path}")

    
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

"""
========================
 E3 AND SSH MATERIALS
========================
"""

# ENV VARIABLE SETUP
ENV_CHID = os.getenv('CHID')
E3_HOSTNAME = "e3-login.tch.harvard.edu"
SSH_DIRECTORY = os.path.join(PROJECT_DIRECTORY, ".ssh")

# E3 PATHS
E3_PROJECT_PATH = "/lab-share/Neuro-Cohen-e2/Public/projects/ADHD_NFB"
E3_LOCALIZER_DIR = os.path.join(E3_PROJECT_PATH, "localizer_data")
E3_PATH_TO_MNI_ACC = os.path.join(E3_LOCALIZER_DIR, "mni_acc_mask.nii.gz")
E3_PATH_TO_MNI_RIFG = os.path.join(E3_LOCALIZER_DIR, "mni_rIFG_mask.nii.gz")
E3_PATH_TO_MNI_MOTOR = os.path.join(E3_LOCALIZER_DIR, "mni_motor_mask.nii.gz")
E3_PATH_TO_MNI_BRAIN = os.path.join(E3_LOCALIZER_DIR, "mni_brain.nii.gz")
E3_PATH_TO_SEGMENTED_BRAIN = os.path.join(E3_LOCALIZER_DIR, "synthseg_mni_brain.nii.gz")
E3_PATH_TO_IP_LOG = os.path.join(E3_LOCALIZER_DIR, "ip_list.txt")
E3_REGISTRATION_DIR = os.path.join(E3_LOCALIZER_DIR, "e3_registration_script")
E3_PATH_TO_INPUT_FUNC_DATA = os.path.join(E3_REGISTRATION_DIR, "input_data")
E3_PATH_TO_TEMP_DIR = os.path.join(E3_REGISTRATION_DIR, "tmp_outdir")

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
check_for_paths(this_script_path=__file__)