# PATHS
SAMBASHARE_DIR_PATH: str = "/workdir/tasks_run/data/sambashare"
ROI_MASK_DIR_PATH: str = "/workdir/tasks_run/data/roi_masks"
LOGGING_DIR_PATH: str = "/workdir/tasks_run/data/logs"
NIFTI_TMP_OUTDIR: str = "/workdir/tasks_run/data/nifti_tmpdir"

# All Script Variables
repetitionTime: float = 1.06

# RIFG EXPERIMENTAL PARAMS
RIFG_N_TRIALS: int = 10
ISI_MIN: int = 250  # in ms
ISI_MAX: int = 1250  # in ms
ISI_STEP: int = 250  # in ms
RANDOM_SEED_VALUE: int = 42

# NFB EXPERIMENTAL PARAMS
NFB_N_TRIALS: int = 140
STARTING_BLOCK_NUM: int = 1
RETRIES_BEFORE_ENDING: int = 3
WINDOW_SIZE: int = 24
START_REST_TRIAL: int = 1
START_NF_TRIAL: int = 20