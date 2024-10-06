#!/bin/bash
# shellcheck disable=SC2034

# ------------ All Task Settings ------------
# Task parameters
REPETITION_TIME=1.06
REST_DURATION=30

# Inter-trial error handling
MAX_RETRIES=3
WAIT_BEFORE_RETRY=0.25
TRIES_BEFORE_NEW_DCM=2

# Screen parameters
SECOND_MONITOR_WIDTH=1920
SECOND_MONITOR_HEIGHT=1080
# Position the second monitor to the right of the first monitor
MONITOR_X_OFFSET=1920
MONITOR_Y_OFFSET=0

FIXATION_WIDTH=200
FIXATION_HEIGHT=200
FIX_LOCATION_SECMON_WIDTH_DIVISOR=2.0
FIX_LOCATION_SECMON_HEIGHT_DIVISOR=2.0
FIX_LOCATION_WIDTH_DIVISOR=2
# FIX_LOCATION_HEIGHT_DIVISOR seemingly not used
FIX_LOCATION_HEIGHT_DIVISOR=2
FIX_RECT_REST_DIVISORS=(2 2)
FONT_COLOR=(255 255 255)

# User Messages
INTER_TRIAL_MESSAGE=("" "Please wait for next steps ..." "")
ENDING_MESSAGE="You have now completed the task. Thank you for participating!"

# Paths
DOCKER_PATH_TO_SETTINGS=/workdir/tasks_run/scripts/settings.py
TMP_OUTDIR_PATH=/workdir/tasks_run/tmp_outdir
SAMBASHARE_DIR_PATH=/workdir/tasks_run/data/sambashare
DATA_DIR_PATH=/workdir/tasks_run/data
FIXATION_PATH=/workdir/tasks_run/rifg_materials/fixationcross.png
PATH_TO_STARTUP_SCRIPT=/workdir/startup_docker.sh
PATH_TO_ALIAS_SCRIPT=/workdir/supporting_scripts/aliases_and_functions.sh
PATH_TO_SSH_MAKER=/workdir/get_ssh_keys.sh
PATH_TO_VENV_MAKER=/workdir/make_venv.sh
PATH_TO_FNIRT_REGISTRATION_SCRIPT=/workdir/tasks_run/scripts/RegisterFnirt.sh
PATH_TO_E3_PREPROC_REGISTRATION_SCRIPT=/workdir/tasks_run/scripts/PreprocRegisterE3.sh
PATH_TO_TRANSFER_FILES_SCRIPT=/workdir/tasks_run/scripts/TransferFilesE3.sh
PATH_TO_COMPARE_SETTINGS_SCRIPT=/workdir/tasks_run/scripts/CompareSettingsDifferences.sh

