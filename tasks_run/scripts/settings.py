import os
import warnings
import sys
"""
================================================================================================

FUNCTIONS 

================================================================================================
"""


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
================================================================================================

USER VARIABLES AND MAIN VARIABLES 

================================================================================================
"""

USER=os.getenv('USER')
ENV_CHID = os.getenv('CHID')      
LOCAL_MASK_DIR_PATH = os.getenv('LOCAL_MASK_DIR_PATH') # Passed as an env to the e3 remote script
HOST_MACHINE_IP = "192.168.2.6"
MRI_SCANNER_IP = "192.168.2.1"

"""
================================================================================================

MAIN DIRECTORY PATHS

================================================================================================

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

SAMBASHARE_DIR_PATH = os.path.join(PROJECT_DIRECTORY, "sambashare") 

DOCKER_RUN_PATH = os.path.join(PROJECT_DIRECTORY, "docker_run")

PERMISSION_SETTING_DIR=os.path.join(DOCKER_RUN_PATH, "set_permissions")

TMP_OUTDIR_PATH = os.path.join(TASKS_RUN_PATH, "tmp_outdir")

GIT_DIR_PATH = os.path.join(PROJECT_DIRECTORY, ".git")

DOCKER_PATH_TO_STARTUP_SCRIPT = os.path.join(DOCKER_RUN_PATH, "startup.sh")

USERS_FILE = os.path.join(DOCKER_RUN_PATH, "users.txt")

SAMBA_DOCKER_BOOT_SCRIPT = os.path.join(DOCKER_RUN_PATH, "boot_samba_container.sh")

SAMBA_DOCKER_DIR = os.path.join(PROJECT_DIRECTORY, "setup_samba_docker")

SMB_CONF_FILE_PATH = os.path.join(SAMBA_DOCKER_DIR, "smb.conf")

UTILITY_SCRIPTS_DIR = os.path.join(SCRIPT_DIRECTORY_PATH, "utility_scripts")

POSTHOC_DIRECTORY = os.path.join(UTILITY_SCRIPTS_DIR, "after_scan_scripts")

DICOM_SORTING_LOGDIR = os.path.join(DATA_DIR_PATH, "dcm_sorting_logs")


"""
================================================================================================

ACROSS-TASK VARIABLES / KNOBS / OTHER

================================================================================================

"""
# Metadata Tags and DICOM Sorting material
PRE_MSIT_TASK_METADATA_TAG: str = "func-bold_task-preMSIT"

POST_MSIT_TASK_METADATA_TAG: str = "func-bold_task-postMSIT"

PRE_RIFG_TASK_METADATA_TAG: str = "func-bold_task-preRIFG"

POST_RIFG_TASK_METADATA_TAG: str = "func-bold_task-postRIFG"


NFB1_TASK_METADATA_TAG: str = "func-bold_task-NFB1"

NFB2_TASK_METADATA_TAG: str = "func-bold_task-NFB2"

NFB3_TASK_METADATA_TAG: str = "func-bold_task-NFB3"


REST1_TASK_METADATA_TAG: str = "func-bold_task-rest1"

REST2_TASK_METADATA_TAG: str = "func-bold_task-rest2"

REST3_TASK_METADATA_TAG: str = "func-bold_task-rest3"

REST4_TASK_METADATA_TAG: str = "func-bold_task-rest4"

# DICOM Metadata Variables
TASK_METADATA_TAG = (0x0018, 0x1030)
SERIES_TIME_METADATA_TAG = (0x0008, 0x0031)

# User Messages
INTER_TRIAL_MESSAGE: list = ["", "Please wait for next steps ...", ""]

ENDING_MESSAGE: str = "You have now completed the task. Thank you for participating!"

# Experimental and MNI Parameters
REPETITION_TIME: float = 1.06

RETRIES_BEFORE_ENDING: int = 3

TRIES_BEFORE_NEW_DCM: int = 2

REST_DURATION: int = 30

RANDOM_SEED_VALUE: int = 42

FIXATION_WIDTH: int = 200

FIXATION_HEIGHT: int = 200

FIX_LOCATION_SECMON_WIDTH_DIVISOR: float = 2.0

FIX_LOCATION_SECMON_HEIGHT_DIVISOR: float = 2.0

FIX_LOCATION_WIDTH_DIVISOR: float = 2

FIX_LOCATION_HEIGHT_DIVISOR: float = 2

FIX_RECT_REST_DIVISORS: tuple = (2, 2)

FONT_COLOR: tuple = (255, 255, 255)

# OTHER 
TZ = "America/New_York"

IGNORE_WARNINGS = True

# Permissions-Setting Paths 
PERMISSIONS_SETTING_SCRIPT = os.path.join(PERMISSION_SETTING_DIR, "permissions_setter_script.sh")

RUN_PERMISSIONS_SETTING_SCRIPT = os.path.join(PERMISSION_SETTING_DIR, "run_permissions_setter.sh")

PID_LIST_FILE = os.path.join(DATA_DIR_PATH, "used_participant_ids.txt")

SUBJECT_DATA_DIR = os.path.join(DATA_DIR_PATH, "subject_data")

"""
================================================================================================

UTILITY AND TEST MATERIALS

================================================================================================

"""
# Directories 
LOCAL_VENV_DIR_PATH = os.path.join(DOCKER_RUN_PATH, "local_venv")


# Utility Scripts 
TRANSFER_FILES_SCRIPT = os.path.join(UTILITY_SCRIPTS_DIR, "TransferFilesE3.sh")

CLEAR_DIRS_SCRIPT = os.path.join(UTILITY_SCRIPTS_DIR, "ClearDirs.py")

SSH_COMMAND_SCRIPT = os.path.join(UTILITY_SCRIPTS_DIR, "ssh_to_e3.sh")

TEST_PYGAME_SCRIPT = os.path.join(DOCKER_RUN_PATH, "test_pygame.py")

COMPARE_SETTINGS_SCRIPT = os.path.join(UTILITY_SCRIPTS_DIR, "CompareSettingsDifferences.sh")

MAKE_LOCAL_VENV_SCRIPT = os.path.join(DOCKER_RUN_PATH, "make_local_venv.sh")

MAKE_LOCAL_SSH_KEYS = os.path.join(UTILITY_SCRIPTS_DIR, "get_ssh_keys.sh")

MAKE_SAMBA_USER_SSH_KEYS = os.path.join(UTILITY_SCRIPTS_DIR, "get_ssh_keys_for_samba_user.sh")

# Other files 
LOCAL_VENV_REQUIREMENTS_FILE = os.path.join(DOCKER_RUN_PATH, "local_requirements.txt")

PREDETERMINED_ISI_MAKER_DIR = os.path.join(UTILITY_SCRIPTS_DIR, "Predetermined_ISI")

MONITOR_INFO_CSV_PATH = os.path.join(DOCKER_RUN_PATH, "current_monitor_information.csv")

MONITOR_INFO_SCRIPT = os.path.join(DOCKER_RUN_PATH, "get_screen_info.py")

# vnc server directory 
VNC_SERVER_DIR = os.path.join(DOCKER_RUN_PATH, "vnc_server_material")

VNC_X11_LOG_PATH = os.path.join(VNC_SERVER_DIR, "x11vnc_log.log")

VNC_XVFB_LOG_PATH = os.path.join(VNC_SERVER_DIR, "Xvfb_log.log")

OPEN_VIEWER_SCRIPT = os.path.join(VNC_SERVER_DIR, "open_viewer.sh")

OPEN_VIEWER_SCRIPT_LOG = os.path.join(VNC_SERVER_DIR, "open_viewer_script_log.log")

OPEN_VIEWER_LOG = os.path.join(VNC_SERVER_DIR, "open_viewer_log.log")


# show mri viewer 
MRI_VIEWER_SCRIPT: str = os.path.join(UTILITY_SCRIPTS_DIR, "show_mri_viewer.py")

"""
================================================================================================

E3 AND SSH MATERIALS

================================================================================================
"""

E3_HOSTNAME = "e3-login.tch.harvard.edu"


# E3 Paths
E3_PROJECT_PATH = "/lab-share/Neuro-Cohen-e2/Public/projects/ADHD_NFB"

E3_PHI_PATH = "/lab-share/Neuro-Cohen-e2/Groups/IRB-P00049401"
# ---- New Script Material ----

# E3 Directories
E3_LOCALIZER_DIR = os.path.join(E3_PHI_PATH, "localizer")

E3_PATH_TO_INPUT_DIRECTORIES = os.path.join(E3_LOCALIZER_DIR, "input_dicom_directories")

E3_PATH_TO_OUTPUT_MASK_DIR = os.path.join(E3_LOCALIZER_DIR, "output_subj_space_masks")

E3_PATH_TO_WORKING_DIR = os.path.join(E3_LOCALIZER_DIR, "localizer_working_dir")

E3_LOCALIZER_MATERIAL_DIR = os.path.join(E3_LOCALIZER_DIR, "material")

E3_PATH_TO_FMRIPREP_OUTPUT = os.path.join(E3_PROJECT_PATH, "fmriprep_output")

# Scripts
E3_SETUP_REG_AND_COMPUTE_PATH = os.path.join(E3_LOCALIZER_DIR, "1_store_ip_and_compute_srun.sh")

E3_MAKE_SSH_KEYS = os.path.join(E3_LOCALIZER_DIR, "2_make_ssh_key.sh")

E3_WAIT_FOR_DATA_SCRIPT = os.path.join(E3_LOCALIZER_DIR, "3_wait_for_data.sh")

E3_PREPROCESS_DICOM_DATA = os.path.join(E3_LOCALIZER_DIR, "4_preprocess_DICOM_data.sh")

E3_SETUP_EASYREG = os.path.join(E3_LOCALIZER_DIR, "5_easyreg_setup.sh")

E3_EASYREG_PYTHON_SCRIPT = os.path.join(E3_LOCALIZER_DIR, "6_easyreg_registration.py")

E3_SEND_MASK_TO_LOCAL = os.path.join(E3_LOCALIZER_DIR, "7_send_to_local.sh")

# MNI Brains
E3_PATH_TO_MNI_ACC = os.path.join(E3_LOCALIZER_MATERIAL_DIR, "mni_acc_mask.nii.gz")

E3_PATH_TO_MNI_RIFG = os.path.join(E3_LOCALIZER_MATERIAL_DIR, "mni_rIFG_mask.nii.gz")

E3_PATH_TO_MNI_MOTOR = os.path.join(E3_LOCALIZER_MATERIAL_DIR, "mni_motor_mask.nii.gz")

E3_PATH_TO_MNI_BRAIN = os.path.join(E3_LOCALIZER_MATERIAL_DIR, "mni_brain.nii.gz")

E3_PATH_TO_SEGMENTED_BRAIN = os.path.join(E3_LOCALIZER_MATERIAL_DIR, "synthseg_mni_brain.nii.gz")


# SSH FROM E3 TO DOCKER / LOCAL MACHINE (without a password)
E3_SSH_DIR = os.path.join(E3_PROJECT_PATH, "ssh")

E3_PRIVATE_KEY_PATH = os.path.join(E3_SSH_DIR, f"docker_e3_key_{ENV_CHID}")

E3_CONFIG_PATH = os.path.join(E3_SSH_DIR ,f"config_{ENV_CHID}")

E3_KNOWN_HOSTS_PATH = os.path.join(E3_SSH_DIR, f"known_hosts_{ENV_CHID}")



# SSH FROM  DOCKER / LOCAL TO E3 (without a password)
SSH_DIRECTORY = os.path.join(PROJECT_DIRECTORY, ".ssh")

if ENV_CHID is None:
    LOCAL_PATH_TO_PRIVATE_KEY = None

    LOCAL_PATH_TO_PUBLIC_KEY = None

    LOCAL_PATH_TO_SSH_CONFIG_FILE = None

    LOCAL_PATH_TO_KNOWN_HOSTS_FILE = None

else:
    LOCAL_PATH_TO_PRIVATE_KEY = os.path.join(SSH_DIRECTORY, f"docker_e3_key_{ENV_CHID}")

    LOCAL_PATH_TO_PUBLIC_KEY = os.path.join(SSH_DIRECTORY, f"docker_e3_key_{ENV_CHID}.pub")

    LOCAL_PATH_TO_SSH_CONFIG_FILE = os.path.join(SSH_DIRECTORY, f"config_{ENV_CHID}")

    LOCAL_PATH_TO_KNOWN_HOSTS_FILE = os.path.join(SSH_DIRECTORY, f"known_hosts_{ENV_CHID}")

    SAMBA_USER_PRIVATE_KEY_PATH = os.path.join(SSH_DIRECTORY, f"local_for_samba_user_{ENV_CHID}")



# Other
E3_PATH_TO_IP_LOG = os.path.join(E3_LOCALIZER_MATERIAL_DIR, "ip_list.txt")

# For sending realtime data to e3 after session
E3_PATH_TO_SUBJECT_DATA = os.path.join(E3_PROJECT_PATH, "subject_data")

# ---- Old Script Material (Extra Vars Needed) ----
OLD_REGISTER_EASYREG_FILE_NAME = "OLD_Realtime_PreprocRegisterE3.sh"

E3_PATH_TO_SETTINGS = os.path.join(E3_PHI_PATH, "settings.py")

OLD_E3_LOCALIZER_DIR = os.path.join(E3_PROJECT_PATH, "localizer_data")

E3_COMPUTE_PATH=os.path.join(OLD_E3_LOCALIZER_DIR, "store_ip_and_compute_srun.sh")

E3_PATH_TO_RIFG_LOGS = os.path.join(E3_PROJECT_PATH, "rifg_logs")

E3_PATH_TO_SAMBASHARE = os.path.join(E3_PROJECT_PATH, "sambashare")

E3_PATH_TO_NFB_LOGS = os.path.join(E3_PROJECT_PATH, "nfb_logs")

E3_PATH_TO_MSIT_LOGS = os.path.join(E3_PROJECT_PATH, "msit_logs")

E3_REGISTRATION_DIR = os.path.join(OLD_E3_LOCALIZER_DIR, "e3_registration_script")

E3_PATH_TO_LOCALIZER_DATA_LOGS = os.path.join(OLD_E3_LOCALIZER_DIR, "logs")

E3_PATH_TO_SUBJECT_SPACE_MASKS = os.path.join(OLD_E3_LOCALIZER_DIR, "subj_space_masks")

E3_PATH_TO_INPUT_FUNC_DATA = os.path.join(E3_REGISTRATION_DIR, "input_data")

E3_PATH_TO_TEMP_DIR = os.path.join(E3_REGISTRATION_DIR, "tmp_outdir")

E3_PATH_TO_OUTPUT_MASK = os.path.join(E3_REGISTRATION_DIR, "output_data")

E3_RUN_EASYREG_SCRIPT = os.path.join(E3_REGISTRATION_DIR, "run_easyreg.sh")

E3_EASYREG_INITIALIZE_PATH = os.path.join(E3_REGISTRATION_DIR, "easyreg_initialize.sh")

E3_EASYREG_REGISTRATION_SCRIPT = os.path.join(E3_REGISTRATION_DIR, "easyreg_registration.py")

E3_PUSH_MASK_TO_LOCAL = os.path.join(E3_REGISTRATION_DIR, "push_mask_to_docker.sh")


"""
================================================================================================

REGISTRATION AND LOCALIZER MATERIALS

================================================================================================
"""

# Directories
LOCALIZER_DIR = os.path.join(DATA_DIR_PATH, "localizer_data")

LOCALIZER_SECONDARY_MATERIAL_DIR_PATH = os.path.join(LOCALIZER_DIR, "secondary_localizer_material")

LOCALIZER_LOG_DIR = os.path.join(LOCALIZER_DIR, "logs")

ROI_MASK_DIR_PATH = os.path.join(LOCALIZER_DIR, "subj_space_masks")

MSIT_MATERIAL_DIR = os.path.join(TASKS_RUN_PATH, "msit_materials")

RIFG_MATERIAL_DIR = os.path.join(TASKS_RUN_PATH, "rifg_materials")

# Events Directory

EVENT_CSV_DIR = os.path.join(DATA_DIR_PATH, "event_csvs")

RIFG_EVENT_CSV_DIR = os.path.join(EVENT_CSV_DIR, "rifg_events")

MSIT_EVENT_CSV = os.path.join(EVENT_CSV_DIR, "msit_events/msit_events_with_rest.csv")


# Scripts and Script Names 
LOCALIZER_FILE_NAME = "2_Realtime_Localizer.py"

LOCALIZER_SCRIPT = os.path.join(SCRIPT_DIRECTORY_PATH, LOCALIZER_FILE_NAME)

REGISTER_FNIRT_FILE_NAME = "2_Realtime_RegisterFnirt.sh"

REGISTER_FNIRT_SCRIPT = os.path.join(SCRIPT_DIRECTORY_PATH, REGISTER_FNIRT_FILE_NAME)

REGISTER_EASYREG_FILE_NAME = "2_Realtime_RegisterEasyeg.sh"

REGISTER_EASYREG_SCRIPT = os.path.join(SCRIPT_DIRECTORY_PATH, REGISTER_EASYREG_FILE_NAME)

# Localizer Materials
MNI_BRAIN_PATH = os.path.join(LOCALIZER_DIR, "mni_brain.nii.gz")

MNI_ACC_MASK_PATH = os.path.join(LOCALIZER_DIR, "mni_acc_mask.nii.gz")

MNI_MOTOR_MASK_PATH = os.path.join(LOCALIZER_DIR, "mni_motor_mask.nii.gz")

MNI_RIFG_MASK_PATH = os.path.join(LOCALIZER_DIR, "mni_rIFG_mask.nii.gz")


# Experimental Parameters 
CLUSTER_THRESHOLD = 50

LOCAL_MAXIMA_VOXEL_CUBE_DIM = 3

INITAL_Z_THRESH = 1.5

USER_Z_MIN = 0

USER_Z_MAX = 5

# Local_venv path
LOCAL_CONDA_INSTALLATION_SCRIPT: str = "/usr/local/Caskroom/mambaforge/base/etc/profile.d/conda.sh"


"""
================================================================================================

RIFG MATERIALS

================================================================================================
"""

# Paths and Filenames 
RIFG_SCRIPT_NAME = "1_Task_RIFG.py"

RIFG_TASK_SCRIPT = os.path.join(SCRIPT_DIRECTORY_PATH, RIFG_SCRIPT_NAME)

RIFG_LOG_DIR = os.path.join(DATA_DIR_PATH, "rifg_logs")

RIFG_SCORE_LOG_DIR = os.path.join(RIFG_LOG_DIR, "scores")

RIFG_ANALYZED_LOGS_DIR = os.path.join(RIFG_LOG_DIR, "logs_analyzed")

ISI_DRIFT_ANALYSIS_OUTPUT_DIR = os.path.join(RIFG_ANALYZED_LOGS_DIR, "ISI_drift_analysis")

BUZZ_PATH = os.path.join(RIFG_MATERIAL_DIR, "buzz2.png")

BEAR_PATH = os.path.join(RIFG_MATERIAL_DIR, "mad_lotso.png")

RIFG_KEYPRESS_ICON_PATH = os.path.join(RIFG_MATERIAL_DIR, "keypress_icon.png")

FIXATION_PATH = os.path.join(RIFG_MATERIAL_DIR, "fixationcross.png")


# User Messages
RIFG_INSTRUCTIONS: list = [
    "Welcome to the Task!",
    "Press any button on the grips (except the one under your right thumb!)...",
    "when you see Buzz (the astronaut).",
    "Do NOT press anything when you see Lotso (the pink bear).",
    "When the Fixation Cross (+) appears, please look directly at it.",
    "This task will start and end with 30s of rest.",
    "During rest, you will only see the fixation cross.",
    "Please wait for experimenter to start the experiment..."]

# Experimental Parameters 
RIFG_N_TRIALS: int = 192

RIFG_N_DICOMS: int = 294

ISI_MIN = 0.25  # in s

ISI_MAX = 1.25  # in s

ISI_STEP = 0.25  # in s

RIFG_TRIAL_DURATION = 0.5 # in s

PREDETERMINED_ISI = 1000 # in ms

RIFG_PRE_SEED = 12345

RIFG_POST_SEED = 111213

RIFG_PRACTICE_SEED = 56789

RIFG_preRIFG_ISI = os.path.join(RIFG_MATERIAL_DIR, "ISI_preRIFG.csv")

RIFG_postRIFG_ISI = os.path.join(RIFG_MATERIAL_DIR, "ISI_postRIFG.csv")

# Projection Parameters

# Buzz and Bear
BUZZ_WIDTH_DIVISOR: int = 5.5  # divisor used to determine the size of new_width_buzz relative to the width of the second monitor.

BUZZ_HEIGHT_DIVISOR: int = 2.5

BEAR_WIDTH_DIVISOR: int = 6

BEAR_HEIGHT_DIVISOR: int = 3

BUZZ_BEAR_LOCATION_SECMON_WIDTH_DIVISOR: float = 2

BUZZ_BEAR_LOCATION_SECMON_HEIGHT_DIVISOR: float = 2

BUZZ_BEAR_LOCATION_WIDTH_DIVISOR: float = 2

BUZZ_BEAR_LOCATION_HEIGHT_DIVISOR: float = 2

# Keypress Words
KEYPRESS_WIDTH: int = 800

KEYPRESS_HEIGHT: int = 200

KEYPRESS_LOCATION_SECMON_WIDTH_DIVISOR: float = 2

KEYPRESS_LOCATION_SECMON_HEIGHT_DIVISOR: float = 3.5

KEYPRESS_LOCATION_WIDTH_DIVISOR: float = 2

KEYPRESS_LOCATION_HEIGHT_DIVISOR: float = 1.5

# Instructions
INSTRUCT_TEXT_RECT_SECMON_WIDTH_DIVISOR: int = 2

INSTRUCT_TEXT_RECT_SECMON_HEIGHT_DIVISOR: int = 4

INSTRUCT_MESSAGE_FONT_SIZE: int = 48

INSTRUCT_Y_OFFSET: int = 100

INSTRUCT_Y_OFFSET_INCREMENT: int = 60

# Exit Message
DISPLAY_EXIT_MESSAGE_TIME: int = 5

EXIT_MESSAGE_FONT_SIZE: int = 55


"""
================================================================================================

NEUROFEEDBACK MATERIALS

================================================================================================
"""
# Paths and Filenames 
NFB_SCRIPT_NAME = "1_Task_NFB.py"

NFB_TASK_SCRIPT = os.path.join(SCRIPT_DIRECTORY_PATH, NFB_SCRIPT_NAME)

NFB_LOG_DIR = os.path.join(DATA_DIR_PATH, "nfb_logs")

NFB_SCORE_LOG_DIR = os.path.join(NFB_LOG_DIR, "scores")

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

# User Messages
NFB_INSTRUCTIONS: list = ["Welcome to the Task!", "Please try to make the rocket go into the portal"]

BLOCK_START_MESSAGE: list = ["", "Starting new block...", ""]

# Experimental and MRI Parameters
NFB_FROM_MEAN_ACTIVATION: bool = True   # Choose one type of NFB, make the other false

NFB_FROM_RESIDUAL_VALUE: bool = False # Choose one type of NFB, make the other false

NFB_N_TRIALS_ODD_BLOCK: int = 140

NFB_N_TRIALS_EVEN_BLOCK: int = 160

STARTING_BLOCK_NUM: int = 1

TRIAL_WINDOW_SIZE: int = 24

START_REST_TRIAL: int = 1

START_NF_TRIAL: int = 20

EVEN_BLOCK_START_2ND_REST: int = 141

TRIALS_BEFORE_STREAK_REPORT: int = 3

# Projection Parameters

# Rocket
ROCKET_WIDTH: int = 250

ROCKET_HEIGHT: int = 250

ROCKET_FLAMES_WIDTH: float = ROCKET_WIDTH * 1.3208  # I calculated that the flames make the ball 32.08% longer, so allocate 32.08% more pixels on the width dimension

ROCKET_FLAMES_HEIGHT: int = 250

INITIAL_ROCKET_LOCATION_SECMON_WIDTH_DIVISOR: float = 2

INITIAL_ROCKET_LOCATION_SECMON_HEIGHT_DIVISOR: float = 2

ROCKET_WIDTH_LOCATION_DIVISOR: float = 2

ROCKET_HEIGHT_LOCATION_DIVISOR: float = 2

# Collision 
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

# Streak
STREAK_WIDTH: int = 600

STREAK_HEIGHT: int = 400

STREAK_LOCATION_DIVISORS: tuple = (2.2, 2, 2.5, 2)

# Portal
PORTAL_WIDTH: int = 500

PORTAL_HEIGHT: int = 600

PORTAL_LOCATION_SECMON_WIDTH_DIVISOR: float = 1.2

PORTAL_LOCATION_SECMON_HEIGHT_DIVISOR: float = 2

PORTAL_WIDTH_LOCATION_DIVISOR: float = 2

PORTAL_HEIGHT_LOCATION_DIVISOR: float = 2

# Background for Words
PRINT_BG_LOCATION_DIVISORS: list = [2, 2, 5.25, 5]

PRINT_LEVEL_LOCATION_DIVISORS: list = [2, 2, 5, 5.5]


"""
================================================================================================

MSIT MATERIALS

================================================================================================
"""
MSIT_SCRIPT_NAME = "1_Task_MSIT.py"
MSIT_TASK_SCRIPT = os.path.join(SCRIPT_DIRECTORY_PATH, MSIT_SCRIPT_NAME)

# PATHS
MSIT_LOG_DIR = os.path.join(DATA_DIR_PATH, "msit_logs")
MSIT_ANALYZED_LOGS_DIR = os.path.join(MSIT_LOG_DIR, "logs_analyzed")
MSIT_SCORE_LOG_DIR = os.path.join(MSIT_LOG_DIR, "scores")
MSIT_GRIPS = os.path.join(MSIT_MATERIAL_DIR, "MRI_grips_button_presses.jpeg")
MSIT_INSTRUCTIONS_PNG = os.path.join(MSIT_MATERIAL_DIR, "msit_instructions_diagram.png") 

# USER MESSAGES
MSIT_INSTRUCTIONS = [
    "Welcome to the MSIT Task! ",
    "Please indicate which number is different from the numbers shown on the screen.",
    "If it's 1 -> press the button under your left index finger. ",
    "If it's 2 -> press the button under your left thumb.",
    "If it's 3 -> press the button under your right index finger.",
    "If you miss one, don't worry, just keep going!",
    "When the Fixation Cross (+) appears, please look directly at it.",
    "Please wait for the experimenters to start the experiment..."
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
MSIT_PRACTICE_SEED = 94

"""
================================================================================================

REST MATERIALS

================================================================================================
"""
REST_SCRIPT_NAME = "1_Task_REST.py"
REST_TASK_SCRIPT = os.path.join(SCRIPT_DIRECTORY_PATH, REST_SCRIPT_NAME)
REST_LOG_DIR = os.path.join(DATA_DIR_PATH, "rest_logs")
REST_SCORE_LOG_DIR = os.path.join(REST_LOG_DIR, "scores")

REST_TASK_DURATION: int = 300  # 5 min in seconds
REST_INSTRUCTIONS: list = [f"Starting the rest task.",
                           "You will see a fixation cross for the duration of the task.",
                           "Please look directly the fixation cross."
                           f"This task will take approximately {round((REST_TASK_DURATION/60), 2)} minutes",
                           "Please wait for experimenter to start the task..."]

REST_MESSAGE_AFTER_DONE: list = [f"This task is complete! Please wait for experimenter ..."]

"""
================================================================================================

AFTER SCAN MATERIALS

================================================================================================
"""

AFTER_SCAN_SCRIPTS_DIR = os.path.join(UTILITY_SCRIPTS_DIR, "after_scan_scripts")
LOG_ANALYSIS_SCRIPT_NAME = "log_output_analysis.py"
ISI_CALCULATION_SCRIPT_NAME = "calculate_rifg_ISI_drift.py"
OUTPUT_LOG_ANALYSIS_SCRIPT = os.path.join(AFTER_SCAN_SCRIPTS_DIR, LOG_ANALYSIS_SCRIPT_NAME)
ISI_DRIFT_CALCULATION_SCRIPT = os.path.join(AFTER_SCAN_SCRIPTS_DIR, ISI_CALCULATION_SCRIPT_NAME)
DICOM_SORTING_SCRIPT_FILENAME = os.path.join(AFTER_SCAN_SCRIPTS_DIR, "sort_dcm_data.py")
PACKAGE_SUBJECT_DATA_SCRIPT = os.path.join(AFTER_SCAN_SCRIPTS_DIR, "package_subject_data.py")
RUN_FMRIPREP_SCRIPT = os.path.join(AFTER_SCAN_SCRIPTS_DIR, "run_fmriprep.py")


""""
================================================================================================

GUI MATERIAL 

================================================================================================
"""

GUI_DIR = os.path.join(PROJECT_DIRECTORY, "nfb_gui")
GUI_DOCKER_RUN_COMMAND = os.path.join(GUI_DIR, "docker_run_command.sh")
GUI_STARTUP_SCRIPT = os.path.join(GUI_DIR, "gui_startup.sh")
GUI_RUN_SCRIPT = os.path.join(GUI_DIR, "run_gui.sh")
GUI_POM_PATH = os.path.join(GUI_DIR, "pom.xml")
GUI_XVFB_LOG =  os.path.join(GUI_DIR, "xvfb.log")
GUI_X11_LOG =  os.path.join(GUI_DIR, "x11vnc.log")
GUI_NFB_LOGO = os.path.join(GUI_DIR, "Neurofeedback_Logo.png")

"""
================================================================================================

SETTINGS FUNCTION MATERIALS

================================================================================================
"""

if __name__ == "__main__":
    run_functions(arguments=sys.argv[1:], 
                  this_script_path=SETTINGS_PATH, 
                  docker_workdir_name=DOCKER_WORKDIR_NAME,
                  PROJECT_DIRECTORY=PROJECT_DIRECTORY)


