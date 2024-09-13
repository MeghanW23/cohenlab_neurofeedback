import pygame
pygame.font.init()


FIXATION_PATH: str = "/Users/sofiaheras/Desktop/NF/go_nogo/fixationcross.png"


FIXATION_WIDTH: int = 200
FIXATION_HEIGHT: int = 200
FIX_LOCATION_SECMON_WIDTH_DIVISOR: float = 2.1
FIX_LOCATION_SECMON_HEIGHT_DIVISOR: float = 2.3
FIX_LOCATION_WIDTH_DIVISOR: float = 2
FIX_LOCATION_HEIGHT_DIVISOR: float = 2
FONT_COLOR: tuple = (255, 255, 255)
FIX_RECT_REST_DIVISORS: tuple = (2, 2)

SECOND_MONITOR_WIDTH: int = 1920
SECOND_MONITOR_HEIGHT: int = 1080
MONITOR_X_OFFSET: int = 1920  # Position the second monitor to the right of the first monitor
MONITOR_Y_OFFSET: int = 0
DATA_DIR: str = "/Users/sofiaheras/Desktop/NF/msit_data"




FONT = pygame.font.Font("/Users/sofiaheras/Desktop/NF/SpaceGrotesk-VariableFont_wght.ttf", 36)



"""
# Set initial position of the ball
initial_ball_x = second_monitor_width // 2 - ball_width // 2
ball_y = SCREEN_HEIGHT // 2 - ball_height // 2
print(f"Initial Ball Location: {initial_ball_x}, {ball_y}")
"""