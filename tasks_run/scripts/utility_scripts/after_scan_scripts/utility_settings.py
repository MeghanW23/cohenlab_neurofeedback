import os

UTILITY_SCRIPTS_DIR = "/workdir/tasks_run/scripts/utility_scripts"
MSIT_LOG_DIR ="/workdir/tasks_run/data/msit_logs"
RIFG_LOG_DIR ="/workdir/tasks_run/data/rifg_logs"

"""
================================================================================================

OUTPUT LOG ANALYSIS MATERIALS
================================================================================================
"""
OUTPUT_LOG_ANALYSIS_SCRIPT_NAME = "log_output_analysis.py"
OUTPUT_LOG_ANALYSIS_SCRIPT_PATH = os.path.join(UTILITY_SCRIPTS_DIR, "after_scan_scripts")
OUTPUT_LOG_ANALYSIS_SCRIPT = os.path.join (OUTPUT_LOG_ANALYSIS_SCRIPT_PATH, OUTPUT_LOG_ANALYSIS_SCRIPT_NAME)
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