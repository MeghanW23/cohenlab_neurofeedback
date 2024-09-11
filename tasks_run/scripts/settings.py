# PATHS
SAMBASHARE_DIR_PATH: str = "/workdir/tasks_run/data/sambashare"
ROI_MASK_DIR_PATH: str = "/workdir/tasks_run/data/roi_masks"
LOGGING_DIR_PATH: str = "/workdir/tasks_run/data/nfb_logs"
NIFTI_TMP_OUTDIR: str = "/workdir/tasks_run/data/nifti_tmpdir"

# All Script Variables
repetitionTime: float = 1.06
RETRIES_BEFORE_ENDING: int = 3
RETRY_WAIT_TIME: float = 0.25
TRIES_BEFORE_NEW_DCM: int = 2

# RIFG EXPERIMENTAL PARAMS
RIFG_N_TRIALS: int = 10
ISI_MIN: int = 250  # in ms
ISI_MAX: int = 1250  # in ms
ISI_STEP: int = 250  # in ms
RANDOM_SEED_VALUE: int = 42

RIFG_OUTDIR: str = "/workdir/tasks_run/data/rifg_logs"
BUZZ_PATH: str = "/workdir/tasks_run/rifg_materials/buzz.png"
ALIEN_PATH: str = "/workdir/tasks_run/rifg_materials/alien.png"
FIXATION_PATH: str = "/workdir/tasks_run/rifg_materials/fixationcross.png"
PRESSED_A_PATH: str = "/workdir/tasks_run/rifg_materials/pressed_a.png"

FIXATION_WIDTH: int = 200
FIXATION_HEIGHT: int = 200
KEYPRESS_WIDTH: int = 600
KEYPRESS_HEIGHT: int = 400
RIFG_FONT_COLOR: tuple = (255, 255, 255)

# NFB EXPERIMENTAL PARAMS
NFB_N_TRIALS: int = 140
STARTING_BLOCK_NUM: int = 1
WINDOW_SIZE: int = 24
START_REST_TRIAL: int = 1
START_NF_TRIAL: int = 20