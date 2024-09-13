import pygame
from typing import Tuple
import settingsSH
import os
import time
import Logger
import ScriptManager
# Create a decorator to check for keypresses
def get_monitor_info(dictionary: dict) -> Tuple[dict, pygame.Surface]:
    # Set up display
    screen_info: pygame.display.Info = pygame.display.Info()
    SCREEN_WIDTH: float = screen_info.current_w
    SCREEN_HEIGHT: float = screen_info.current_h
    Logger.print_and_log(f"experimenter screen width: {SCREEN_WIDTH}")
    Logger.print_and_log(f"experimenter screen height: {SCREEN_HEIGHT}")

    dictionary["whole_session_data"]["experimenter_screen_width"]: float = SCREEN_WIDTH
    dictionary["whole_session_data"]["experimenter_screen_height"]: float = SCREEN_HEIGHT
    dictionary["whole_session_data"]["second_monitor_width"]: float = settingsSH.SECOND_MONITOR_WIDTH
    dictionary["whole_session_data"]["second_monitor_height"]: float = settingsSH.SECOND_MONITOR_HEIGHT
    dictionary["whole_session_data"]["monitor_X_OFFSET"]: float = settingsSH.MONITOR_X_OFFSET
    dictionary["whole_session_data"]["monitor_Y_OFFSET"]: float = settingsSH.MONITOR_Y_OFFSET

    Logger.print_and_log(f"Second monitor resolution: {settingsSH.SECOND_MONITOR_WIDTH}x{settingsSH.SECOND_MONITOR_HEIGHT}")

    # Set the display position (offset from the primary display)
    os.environ['SDL_VIDEO_WINDOW_POS'] = f'{settingsSH.MONITOR_X_OFFSET},{settingsSH.MONITOR_Y_OFFSET}'

    screen: pygame.Surface = pygame.display.set_mode((dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]), pygame.FULLSCREEN | pygame.NOFRAME)

    return dictionary, screen

def show_end_message(screen: pygame.Surface):
    Logger.print_and_log(f"SUBJECT IS DONE. DISPLAYING EXIT MESSAGE FOR {settingsSH.DISPLAY_EXIT_MESSAGE_TIME}")

    font: pygame.font.Font = pygame.font.Font(None, settingsSH.FONT)
    text: pygame.Surface = font.render(settingsSH.ENDING_MESSAGE, True, settingsSH.FONT_COLOR)  # White text
    text_rect: pygame.Rect = text.get_rect(center=(settingsSH.SECOND_MONITOR_WIDTH // settingsSH.INSTRUCT_TEXT_RECT_SECMON_WIDTH_DIVISOR, settingsSH.SECOND_MONITOR_HEIGHT // settingsSH.INSTRUCT_TEXT_RECT_SECMON_HEIGHT_DIVISOR))  # Centered text

    screen.fill((0, 0, 0))
    screen.blit(text, text_rect)

    pygame.display.flip()

    time.sleep(settingsSH.DISPLAY_EXIT_MESSAGE_TIME)  # show the message on screen for 5 seconds

def show_instructions(screen: pygame.Surface, instructions: list) -> None:
    Logger.print_and_log("Showing Instructions. Task will start when 's' is pressed (scanner key maps to s on mac, so starting the experiment will trigger the task)")
    font: pygame.font.Font = pygame.font.Font(None, settingsSH.INSTRUCT_MESSAGE_FONT_SIZE)
    # Render and display each line of instructions
    screen.fill((0, 0, 0))

    for line in instructions:
        text: pygame.Surface = font.render(line, True, settingsSH.FONT_COLOR)  # White text
        text_rect: pygame.Rect = text.get_rect(center=(settingsSH.SECOND_MONITOR_WIDTH // settingsSH.INSTRUCT_TEXT_RECT_SECMON_WIDTH_DIVISOR, settingsSH.INSTRUCT_Y_OFFSET))
        screen.blit(text, text_rect)
        settingsSH.INSTRUCT_Y_OFFSET += settingsSH.INSTRUCT_Y_OFFSET_INCREMENT  # Increment y-position for each new line
        # settingsSH.INSTRUCT_Y_OFFSET += line_height

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                return None
            else:
                time.sleep(0.1)

def initialize_screen(screen: pygame.Surface, instructions: list):
    Logger.print_and_log("TO SHOW INSTRUCTIONS, PLEASE PRESS 'r'.")
    font: pygame.font.Font = pygame.font.Font(None, settingsSH.INSTRUCT_MESSAGE_FONT_SIZE)

    # Render and display each line of instructions
    screen.fill((0, 0, 0))

    for line in instructions:
        text: pygame.Surface = font.render(line, True, settingsSH.FONT_COLOR)  # White text
        text_rect: pygame.Rect = text.get_rect(center=(settingsSH.SECOND_MONITOR_WIDTH // settingsSH.INSTRUCT_TEXT_RECT_SECMON_WIDTH_DIVISOR, settingsSH.INSTRUCT_Y_OFFSET))
        screen.blit(text, text_rect)
        settingsSH.INSTRUCT_Y_OFFSET += settingsSH.INSTRUCT_Y_OFFSET_INCREMENT  # Increment y-position for each new line
        # settingsSH.INSTRUCT_Y_OFFSET += line_height

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                return None
            else:
                time.sleep(0.1)

def project_nfb_trial(dictionary: dict, screen: pygame.Surface) -> dict:
    current_block, current_trial = ScriptManager.dict_get_most_recent(dictionary=dictionary, get="both")
    portal_image: pygame.Surface = pygame.image.load(settingsSH.PORTAL_PATH)
    collision: pygame.Surface = pygame.image.load(settingsSH.COLLISION_WORD_ART)
    streak: pygame.Surface = pygame.image.load(settingsSH.HIGH_PERFORM_WORD_ART)
    print_bg: pygame.Surface = pygame.image.load(settingsSH.PRINT_BACKGROUND)
    rocket_image: pygame.Surface = pygame.image.load(settingsSH.ROCKET_PATH)
    rocket_image_flames: pygame.Surface = pygame.image.load(settingsSH.ROCKET_WITH_FLAMES_PATH)
    bg = pygame.transform.scale(pygame.image.load(settingsSH.BACKGROUND_PATH_1).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))
    bg2 = pygame.transform.scale(pygame.image.load(settingsSH.BACKGROUND_PATH_2).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))
    bg3 = pygame.transform.scale(pygame.image.load(settingsSH.BACKGROUND_PATH_3).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))
    bg4 = pygame.transform.scale(pygame.image.load(settingsSH.BACKGROUND_PATH_4).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))

    rocket_image: pygame.Surface = pygame.transform.scale(rocket_image, (settingsSH.rocket_width, settingsSH.rocket_height))
    rocket_image_flames:  pygame.Surface = pygame.transform.scale(rocket_image_flames,(settingsSH.rocket_flames_width, settingsSH.rocket_flames_height))
    portal_image: pygame.Surface = pygame.transform.scale(portal_image, (settingsSH.portal_width, settingsSH.portal_height))

    # Set initial position of the rocket
    initial_rocket_x = dictionary["whole_session_data"]["second_monitor_width"] // settingsSH.INITIAL_ROCKET_LOCATION_SECMON_WIDTH_DIVISOR - settingsSH.rocket_width // settingsSH.ROCKET_WIDTH_LOCATION_DIVISOR
    rocket_y = dictionary["whole_session_data"]["second_monitor_height"] // settingsSH.INITIAL_ROCKET_LOCATION_SECMON_HEIGHT_DIVISOR - settingsSH.rocket_height // settingsSH.ROCKET_WIDTH_LOCATION_DIVISOR
    portal_x = dictionary["whole_session_data"]["second_monitor_width"] // settingsSH.PORTAL_LOCATION_SECMON_WIDTH_DIVISOR - settingsSH.portal_width // settingsSH.PORTAL_WIDTH_LOCATION_DIVISOR
    portal_y = dictionary["whole_session_data"]["second_monitor_height"] // settingsSH.PORTAL_LOCATION_SECMON_HEIGHT_DIVISOR - settingsSH.portal_height // settingsSH.PORTAL_HEIGHT_LOCATION_DIVISOR

    if current_trial == "trial1":
        dictionary[current_block]["rocket_x"]: float = initial_rocket_x

    screen.fill((0, 0, 0))

    if "current_level" not in dictionary[current_block]:
        dictionary[current_block]["current_level"]: int = 1
    if "collision_count" not in dictionary[current_block]:
        dictionary[current_block]["collision_count"]: int = 0

    print(f"SUBJECT IS AT LEVEL #{dictionary[current_block]['current_level']}")
    if dictionary[current_block]["current_level"] <= 1:
        screen.blit(bg, (0, 0))
    elif dictionary[current_block]["current_level"] == 2:
        screen.blit(bg2, (0, 0))
    elif dictionary[current_block]["current_level"] == 3:
        screen.blit(bg3, (0, 0))
    else:
        screen.blit(bg4, (0, 0))

    # Level Words
    print_level = settingsSH.FONT.render(f"Level: {dictionary[current_block]['current_level']}, Portals Reached: {dictionary[current_block]['collision_count']}", True, settingsSH.FONT_COLOR)  # Text, antialiasing, color
    print_width, print_height = print_level.get_size()
    print_bg = pygame.transform.scale(print_bg, (print_width * 2, print_height * 2))

    # background must be blit before print
    screen.blit(print_bg, (dictionary["whole_session_data"]["second_monitor_width"] // settingsSH.PRINT_BG_LOCATION_DIVISORS[0] - print_bg.get_width() // settingsSH.PRINT_BG_LOCATION_DIVISORS[1], dictionary["whole_session_data"]["second_monitor_height"] // settingsSH.PRINT_BG_LOCATION_DIVISORS[2] - print_bg.get_height() // settingsSH.PRINT_BG_LOCATION_DIVISORS[3]))
    screen.blit(print_level, (dictionary["whole_session_data"]["second_monitor_width"] // settingsSH.PRINT_LEVEL_LOCATION_DIVISORS[0] - print_level.get_width() // settingsSH.PRINT_LEVEL_LOCATION_DIVISORS[1], dictionary["whole_session_data"]["second_monitor_height"] // settingsSH.PRINT_LEVEL_LOCATION_DIVISORS[2] - print_level.get_height() // settingsSH.PRINT_LEVEL_LOCATION_DIVISORS[3]))

    if "rocket_x" in dictionary[current_block]:
        if dictionary[current_block]["rocket_x"] >= (portal_x * 0.9):  # collision
            dictionary[current_block]["collision_count"] += 1
            dictionary[current_block]["rocket_x"] = 0
            screen.blit(collision, (dictionary["whole_session_data"]["second_monitor_width"] // settingsSH.COLLISION_DIVISORS[0] - collision.get_width() // settingsSH.COLLISION_DIVISORS[1], dictionary["whole_session_data"]["second_monitor_height"] // settingsSH.COLLISION_DIVISORS[2] - collision.get_height() // settingsSH.COLLISION_DIVISORS[3]))

    screen.blit(portal_image, (portal_x, portal_y))

    pygame.display.flip()

    return dictionary

def show_fixation_cross(dictionary: dict, screen: pygame.Surface):
    fixation: pygame.Surface = pygame.image.load(settingsSH.FIXATION_PATH)

    screen.fill((0, 0, 0))  # fill the screen black

    new_width_fixation: float = settingsSH.FIXATION_WIDTH
    new_height_fixation: float = settingsSH.FIXATION_HEIGHT
    fix_resized: pygame.Surface = pygame.transform.scale(fixation, (new_width_fixation, new_height_fixation))
    fixation_width: float = fix_resized.get_width()
    fixation_height: float = fix_resized.get_height()
    dictionary["whole_session_data"]["fixation_width"]: float = fixation_width
    dictionary["whole_session_data"]["fixation_height"]: float = fixation_height

    screen.blit(fix_resized, (settingsSH.SECOND_MONITOR_WIDTH // settingsSH.FIX_LOCATION_SECMON_WIDTH_DIVISOR -
                              fixation_width // settingsSH.FIX_LOCATION_WIDTH_DIVISOR,
                              settingsSH.SECOND_MONITOR_HEIGHT // settingsSH.FIX_LOCATION_SECMON_HEIGHT_DIVISOR -
                              fixation_height // settingsSH.FIX_LOCATION_WIDTH_DIVISOR))  # show fixation cross

    pygame.display.flip()  # flip to monitor

def show_fixation_cross_rest(screen):
   fixation_cross = pygame.image.load("/User/sofiaheras/Desktop/NF/go_nogo/fixationcross.png")

   new_width_fixation: float = settingsSH.FIXATION_WIDTH
   new_height_fixation: float = settingsSH.FIXATION_HEIGHT

   fixation_cross = pygame.transform.scale(fixation_cross, (new_width_fixation, new_height_fixation))
   screen_width, screen_height = screen.get_size()

   fix_rect = fixation_cross.get_rect()
   fix_rect.center = (screen_width // settingsSH.FIX_RECT_REST_DIVISORS[0], screen_height // settingsSH.FIX_RECT_REST_DIVISORS[1])

   end_time = time.time() + settingsSH.REST_DURATION

   # Display the fixation cross image for the specified duration
   while time.time() < end_time:
       # Fill the screen with black
       screen.fill((0, 0, 0))

       # Blit (copy) the resized fixation cross image to the center of the screen
       screen.blit(fixation_cross, fix_rect)

       # Update the display to reflect the changes
       pygame.display.flip()
