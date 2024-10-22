import os
import warnings

"""
Variables assigned here are used in the task scripts. 
The aims for most paths to be relative to this directory so they may be used across computers and both inside and outside docekr containers.
The script will also check for the existance of all (non-e3) paths upon it being called by other scripts. 
If a path is not found, the script will raise a warning to the user
"""

# check for existence of main paths 
def check_for_paths(this_script_path: str): 
    global_vars = globals().copy()

    check_E3_paths = False
    if "Neuro-Cohen-e2" in this_script_path:
        print("Checking for existance of E3 settings paths.")
        check_E3_paths = True 

    for var_name, path_var in global_vars.items():
        if isinstance(path_var, str) and ("\\" in path_var or "/" in path_var):
            if check_E3_paths:
                if "E3" in var_name:
                    if not os.path.exists(path_var):
                        warnings.warn(message=f"Cannot find given path for settings variable {var_name}: {path_var}. Check {var_name} at: {this_script_path}")
            else:
                if not "E3" in var_name:
                    if not os.path.exists(path_var):
                        warnings.warn(message=f"Cannot find given path for settings variable {var_name}: {path_var}. Check {var_name} at: {this_script_path}")
    
"""
========================
 MAIN DIRECTORY PATHS
========================
"""
SCRIPT_DIRECTORY_PATH = os.path.dirname(__file__)

TASKS_RUN_PATH = os.path.dirname(SCRIPT_DIRECTORY_PATH)

DATA_DIR_PATH: str = os.path.join(TASKS_RUN_PATH, "data")

LOCAL_SAMBASHARE_DIR_PATH = "/Users/samba_user/sambashare"
SAMBASHARE_DIR_PATH = os.path.join(DATA_DIR_PATH, "sambashare")
LOCAL_SAMBASHARE_DIR_PATH2 = "/bull/shit/path"

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
 E3 MATERIALS
========================
"""

# ENV VARIABLE SETUP
ENV_CHID = os.getenv('CHID')
E3_HOSTNAME = "e3-login.tch.harvard.edu"
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

check_for_paths(this_script_path=__file__)