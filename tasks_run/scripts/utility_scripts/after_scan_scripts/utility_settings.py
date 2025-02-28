import os

UTILITY_SCRIPTS_DIR = "/workdir/tasks_run/scripts/utility_scripts"
MSIT_LOG_DIR ="/workdir/tasks_run/data/msit_logs"
RIFG_LOG_DIR ="/workdir/tasks_run/data/rifg_logs"

"""
================================================================================================

OUTPUT LOG ANALYSIS MATERIALS
================================================================================================
"""

MSIT_ANALYZED_LOGS_DIR = os.path.join(MSIT_LOG_DIR, "logs_analyzed")
RIFG_ANALYZED_LOGS_DIR = os.path.join(RIFG_LOG_DIR, "logs_analyzed")

"""
================================================================================================

FILE HANDLER MATERIALS
================================================================================================
"""

SAMBASHARE_DIR_PATH= "/workdir/sambashare"
TMP_OUTDIR_PATH = "/workdir/tasks_run/tmp_outdir"
ROI_MASK_DIR_PATH = "/workdir/tasks_run/data/localizer_data/subj_space_masks"