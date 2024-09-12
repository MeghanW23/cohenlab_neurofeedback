import pygame
# All Script Variables
SAMBASHARE_DIR_PATH: str = "/workdir/tasks_run/data/sambashare"
ROI_MASK_DIR_PATH: str = "/workdir/tasks_run/data/roi_masks"
FIXATION_PATH: str = "/workdir/tasks_run/rifg_materials/fixationcross.png"

repetitionTime: float = 1.06
RETRIES_BEFORE_ENDING: int = 3
RETRY_WAIT_TIME: float = 0.25
TRIES_BEFORE_NEW_DCM: int = 2

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
DATA_DIR: str = "/workdir/tasks_run/data"

ENDING_MESSAGE: str = "You have now completed the task. Thank you for participating!"

# RIFG EXPERIMENTAL PARAMS
RIFG_N_TRIALS: int = 10
ISI_MIN: int = 250  # in ms
ISI_MAX: int = 1250  # in ms
ISI_STEP: int = 250  # in ms
RANDOM_SEED_VALUE: int = 42

RIFG_LOG_DIR: str = "/workdir/tasks_run/data/rifg_logs"

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
INSTRUCT_TEXT_RECT_SECMON_HEIGHT_DIVISOR: int = 4
DISPLAY_EXIT_MESSAGE_TIME: int = 5
EXIT_MESSAGE_FONT_SIZE: int = 55
INSTRUCT_MESSAGE_FONT_SIZE: int = 48
INSTRUCT_Y_OFFSET: int = 100
INSTRUCT_Y_OFFSET_INCREMENT: int = 60

RIFG_INSTRUCTIONS: list = [
    "Welcome to the Task!",
    "Press 'A' using your left thumb when you see Buzz (the astronaut).",
    "Do NOT press anything when you see Alien.",
    "Please wait for experimenter to start the experiment..."]

# NFB EXPERIMENTAL PARAMS
NFB_LOG_DIR: str = "/workdir/tasks_run/data/nfb_logs"
NIFTI_TMP_OUTDIR: str = "/workdir/tasks_run/data/nifti_tmpdir"

NFB_N_TRIALS: int = 140
STARTING_BLOCK_NUM: int = 1
WINDOW_SIZE: int = 24
START_REST_TRIAL: int = 1
START_NF_TRIAL: int = 20

NFB_INSTRUCTIONS: list = [
    "Welcome to the Task!",
    "Please try to make the rocket go into the portal"
    ]
FONT = pygame.font.Font('/workdir/tasks_run/nfb_materials/Space_Grotesk/SpaceGrotesk-VariableFont_wght.ttf', 36)

BACKGROUND_PATH_1: str = "/workdir/tasks_run/nfb_materials/background_1.png"
BACKGROUND_PATH_2: str = "/workdir/tasks_run/nfb_materials/background_1.png"
BACKGROUND_PATH_3: str = "/workdir/tasks_run/nfb_materials/background_1.png"
BACKGROUND_PATH_4: str = "/workdir/tasks_run/nfb_materials/background_1.png"

ROCKET_PATH: str = "/workdir/tasks_run/nfb_materials/rocket.png"
ROCKET_WITH_FLAMES_PATH: str = "/workdir/tasks_run/nfb_materials/RocketWithFlames.png"
PORTAL_PATH: str = "/workdir/tasks_run/nfb_materials/portal.png"
PRINT_BACKGROUND: str = "/workdir/tasks_run/nfb_materials/scifi_term.png"
COLLISION_WORD_ART: str = "/workdir/tasks_run/nfb_materials/CollisionWordArt.png"
HIGH_PERFORM_WORD_ART: str = "/workdir/tasks_run/nfb_materials/highPerfText.png"

# change ball image size
rocket_width: int = 250
rocket_height: int = 250
rocket_flames_width: float = rocket_width * 1.3208  # I calculated that the flames make the ball 32.08% longer, so allocate 32.08% more pixels on the width dimension (height is the same though)

collision_width: int = 500
collision_height: int = 100
streak_width: int = 1000
streak_height: int = 250

INITIAL_ROCKET_LOCATION_SECMON_WIDTH_DIVISOR: float = 2
INITIAL_ROCKET_LOCATION_SECMON_HEIGHT_DIVISOR: float = 2
ROCKET_WIDTH_LOCATION_DIVISOR: float = 2
ROCKET_HEIGHT_LOCATION_DIVISOR: float = 2

"""
# Set initial position of the ball
initial_ball_x = second_monitor_width // 2 - ball_width // 2
ball_y = SCREEN_HEIGHT // 2 - ball_height // 2
print(f"Initial Ball Location: {initial_ball_x}, {ball_y}")
"""