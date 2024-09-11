# All Script Variables
SAMBASHARE_DIR_PATH: str = "/workdir/tasks_run/data/sambashare"
ROI_MASK_DIR_PATH: str = "/workdir/tasks_run/data/roi_masks"
FIXATION_PATH: str = "/workdir/tasks_run/rifg_materials/fixationcross.png"

repetitionTime: float = 1.06
RETRIES_BEFORE_ENDING: int = 3
RETRY_WAIT_TIME: float = 0.25
TRIES_BEFORE_NEW_DCM: int = 2
DISPLAY_EXIT_MESSAGE_TIME: int = 5
EXIT_MESSAGE_FONT_SIZE: int = 55
INSTRUCT_MESSAGE_FONT_SIZE: int = 48
INSTRUCT_Y_OFFSET: int = 100
INSTRUCT_Y_OFFSET_INCREMENT: int = 60
FIXATION_WIDTH: int = 200
FIXATION_HEIGHT: int = 200
FIX_LOCATION_SECMON_WIDTH_DIVISOR: float = 2.1
FIX_LOCATION_SECMON_HEIGHT_DIVISOR: float = 2.3
FIX_LOCATION_WIDTH_DIVISOR: float = 2
FIX_LOCATION_HEIGHT_DIVISOR: float = 2
FONT_COLOR: tuple = (255, 255, 255)

SECOND_MONITOR_WIDTH: int = 1920
SECOND_MONITOR_HEIGHT: int = 1080
MONITOR_X_OFFSET: int = 1920  # Position the second monitor to the right of the first monitor
MONITOR_Y_OFFSET: int = 0

# RIFG EXPERIMENTAL PARAMS
RIFG_N_TRIALS: int = 10
ISI_MIN: int = 250  # in ms
ISI_MAX: int = 1250  # in ms
ISI_STEP: int = 250  # in ms
RANDOM_SEED_VALUE: int = 42

RIFG_OUTDIR: str = "/workdir/tasks_run/data/rifg_logs"

BUZZ_PATH: str = "/workdir/tasks_run/rifg_materials/buzz2.png"
BUZZ_WIDTH_DIVISOR: int = 6  # divisor used to determine the size of new_width_buzz relative to the width of the second monitor.
BUZZ_HEIGHT_DIVISOR: int = 3

ALIEN_PATH: str = "/workdir/tasks_run/rifg_materials/alien.png"
ALIEN_WIDTH_DIVISOR: int = 4
ALIEN_HEIGHT_DIVISOR: int = 4

BUZZ_ALIEN_LOCATION_SECMON_WIDTH_DIVISOR: float = 2.1
BUZZ_ALIEN_LOCATION_SECMON_HEIGHT_DIVISOR: float = 2.3
BUZZ_ALIEN_LOCATION_WIDTH_DIVISOR: float = 2
BUZZ_ALIEN_LOCATION_HEIGHT_DIVISOR: float = 2

PRESSED_A_PATH: str = "/workdir/tasks_run/rifg_materials/pressed_a.png"
KEYPRESS_WIDTH: int = 600
KEYPRESS_HEIGHT: int = 400
KEYPRESS_LOCATION_SECMON_WIDTH_DIVISOR: float = 1.9
KEYPRESS_LOCATION_SECMON_HEIGHT_DIVISOR: float = 3.3
KEYPRESS_LOCATION_WIDTH_DIVISOR: float = 2
KEYPRESS_LOCATION_HEIGHT_DIVISOR: float = 2

INSTRUCT_TEXT_RECT_SECMON_WIDTH_DIVISOR: int = 2
INSTRUCT_TEXT_RECT_SECMON_HEIGHT_DIVISOR: int = 2

# NFB EXPERIMENTAL PARAMS
LOGGING_DIR_PATH: str = "/workdir/tasks_run/data/nfb_logs"
NIFTI_TMP_OUTDIR: str = "/workdir/tasks_run/data/nifti_tmpdir"

NFB_N_TRIALS: int = 140
STARTING_BLOCK_NUM: int = 1
WINDOW_SIZE: int = 24
START_REST_TRIAL: int = 1
START_NF_TRIAL: int = 20