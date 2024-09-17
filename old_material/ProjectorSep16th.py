import pygame
from typing import Tuple
import settings
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
    dictionary["whole_session_data"]["second_monitor_width"]: float = settings.SECOND_MONITOR_WIDTH
    dictionary["whole_session_data"]["second_monitor_height"]: float = settings.SECOND_MONITOR_HEIGHT
    dictionary["whole_session_data"]["monitor_X_OFFSET"]: float = settings.MONITOR_X_OFFSET
    dictionary["whole_session_data"]["monitor_Y_OFFSET"]: float = settings.MONITOR_Y_OFFSET

    Logger.print_and_log(f"Second monitor resolution: {settings.SECOND_MONITOR_WIDTH}x{settings.SECOND_MONITOR_HEIGHT}")

    # Set the display position (offset from the primary display)
    os.environ['SDL_VIDEO_WINDOW_POS'] = f'{settings.MONITOR_X_OFFSET},{settings.MONITOR_Y_OFFSET}'

    screen: pygame.Surface = pygame.display.set_mode((dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]), pygame.FULLSCREEN | pygame.NOFRAME)

    return dictionary, screen

def show_end_message(screen: pygame.Surface):
    Logger.print_and_log(f"SUBJECT IS DONE. DISPLAYING EXIT MESSAGE FOR {settings.DISPLAY_EXIT_MESSAGE_TIME}")

    font: pygame.font.Font = pygame.font.Font(None, settings.EXIT_MESSAGE_FONT_SIZE)
    text: pygame.Surface = font.render(settings.ENDING_MESSAGE, True, settings.FONT_COLOR)  # White text
    text_rect: pygame.Rect = text.get_rect(center=(settings.SECOND_MONITOR_WIDTH // settings.INSTRUCT_TEXT_RECT_SECMON_WIDTH_DIVISOR, settings.SECOND_MONITOR_HEIGHT // settings.INSTRUCT_TEXT_RECT_SECMON_HEIGHT_DIVISOR))  # Centered text

    screen.fill((0, 0, 0))
    screen.blit(text, text_rect)

    pygame.display.flip()

    time.sleep(settings.DISPLAY_EXIT_MESSAGE_TIME)  # show the message on screen for 5 seconds

def show_instructions(screen: pygame.Surface, instructions: list) -> None:
    Logger.print_and_log("Showing Instructions. Task will start when 's' is pressed (scanner key maps to s on mac, so starting the experiment will trigger the task)")
    font: pygame.font.Font = pygame.font.Font(None, settings.INSTRUCT_MESSAGE_FONT_SIZE)
    # Render and display each line of instructions
    screen.fill((0, 0, 0))

    for line in instructions:
        text: pygame.Surface = font.render(line, True, settings.FONT_COLOR)  # White text
        text_rect: pygame.Rect = text.get_rect(center=(settings.SECOND_MONITOR_WIDTH // settings.INSTRUCT_TEXT_RECT_SECMON_WIDTH_DIVISOR, settings.INSTRUCT_Y_OFFSET))
        screen.blit(text, text_rect)
        settings.INSTRUCT_Y_OFFSET += settings.INSTRUCT_Y_OFFSET_INCREMENT  # Increment y-position for each new line
        # settings.INSTRUCT_Y_OFFSET += line_height

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                return None
            else:
                time.sleep(0.1)

def initialize_screen(screen: pygame.Surface, instructions: list):
    Logger.print_and_log("TO SHOW INSTRUCTIONS, PLEASE PRESS 'r'.")
    font: pygame.font.Font = pygame.font.Font(None, settings.INSTRUCT_MESSAGE_FONT_SIZE)

    # Render and display each line of instructions
    screen.fill((0, 0, 0))

    for line in instructions:
        text: pygame.Surface = font.render(line, True, settings.FONT_COLOR)  # White text
        text_rect: pygame.Rect = text.get_rect(center=(settings.SECOND_MONITOR_WIDTH // settings.INSTRUCT_TEXT_RECT_SECMON_WIDTH_DIVISOR, settings.INSTRUCT_Y_OFFSET))
        screen.blit(text, text_rect)
        settings.INSTRUCT_Y_OFFSET += settings.INSTRUCT_Y_OFFSET_INCREMENT  # Increment y-position for each new line
        # settings.INSTRUCT_Y_OFFSET += line_height

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                return None
            else:
                time.sleep(0.1)

def project_nfb_trial(dictionary: dict, screen: pygame.Surface) -> dict:
    current_block, current_trial = ScriptManager.dict_get_most_recent(dictionary=dictionary, get="both")
    portal_image: pygame.Surface = pygame.image.load(settings.PORTAL_PATH)
    collision: pygame.Surface = pygame.image.load(settings.COLLISION_WORD_ART)
    streak: pygame.Surface = pygame.image.load(settings.HIGH_PERFORM_WORD_ART)
    print_bg: pygame.Surface = pygame.image.load(settings.PRINT_BACKGROUND)
    rocket_image: pygame.Surface = pygame.image.load(settings.ROCKET_PATH)
    rocket_image_flames: pygame.Surface = pygame.image.load(settings.ROCKET_WITH_FLAMES_PATH)
    bg = pygame.transform.scale(pygame.image.load(settings.BACKGROUND_PATH_1).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))
    bg2 = pygame.transform.scale(pygame.image.load(settings.BACKGROUND_PATH_2).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))
    bg3 = pygame.transform.scale(pygame.image.load(settings.BACKGROUND_PATH_3).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))
    bg4 = pygame.transform.scale(pygame.image.load(settings.BACKGROUND_PATH_4).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))

    rocket_image: pygame.Surface = pygame.transform.scale(rocket_image, (settings.ROCKET_WIDTH, settings.ROCKET_HEIGHT))
    rocket_image_flames:  pygame.Surface = pygame.transform.scale(rocket_image_flames, (settings.ROCKET_FLAMES_WIDTH, settings.ROCKET_FLAMES_HEIGHT))
    portal_image: pygame.Surface = pygame.transform.scale(portal_image, (settings.PORTAL_WIDTH, settings.PORTAL_HEIGHT))

    # Set initial position of the rocket
    initial_rocket_x = dictionary["whole_session_data"]["second_monitor_width"] // settings.INITIAL_ROCKET_LOCATION_SECMON_WIDTH_DIVISOR - settings.ROCKET_WIDTH // settings.ROCKET_WIDTH_LOCATION_DIVISOR
    rocket_y = dictionary["whole_session_data"]["second_monitor_height"] // settings.INITIAL_ROCKET_LOCATION_SECMON_HEIGHT_DIVISOR - settings.ROCKET_HEIGHT // settings.ROCKET_WIDTH_LOCATION_DIVISOR
    portal_x = dictionary["whole_session_data"]["second_monitor_width"] // settings.PORTAL_LOCATION_SECMON_WIDTH_DIVISOR - settings.PORTAL_WIDTH // settings.PORTAL_WIDTH_LOCATION_DIVISOR
    portal_y = dictionary["whole_session_data"]["second_monitor_height"] // settings.PORTAL_LOCATION_SECMON_HEIGHT_DIVISOR - settings.PORTAL_HEIGHT // settings.PORTAL_HEIGHT_LOCATION_DIVISOR

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
    print_level = settings.FONT.render(f"Level: {dictionary[current_block]['current_level']}, Portals Reached: {dictionary[current_block]['collision_count']}", True, settings.FONT_COLOR)  # Text, antialiasing, color
    print_width, print_height = print_level.get_size()
    print_bg = pygame.transform.scale(print_bg, (print_width * 2, print_height * 2))

    # background must be blit before print
    screen.blit(print_bg, (dictionary["whole_session_data"]["second_monitor_width"] // settings.PRINT_BG_LOCATION_DIVISORS[0] - print_bg.get_width() // settings.PRINT_BG_LOCATION_DIVISORS[1], dictionary["whole_session_data"]["second_monitor_height"] // settings.PRINT_BG_LOCATION_DIVISORS[2] - print_bg.get_height() // settings.PRINT_BG_LOCATION_DIVISORS[3]))
    screen.blit(print_level, (dictionary["whole_session_data"]["second_monitor_width"] // settings.PRINT_LEVEL_LOCATION_DIVISORS[0] - print_level.get_width() // settings.PRINT_LEVEL_LOCATION_DIVISORS[1], dictionary["whole_session_data"]["second_monitor_height"] // settings.PRINT_LEVEL_LOCATION_DIVISORS[2] - print_level.get_height() // settings.PRINT_LEVEL_LOCATION_DIVISORS[3]))

    if "rocket_x" in dictionary[current_block]:
        if dictionary[current_block]["rocket_x"] >= (portal_x * 0.9):  # collision
            dictionary[current_block]["collision_count"] += 1
            dictionary[current_block]["rocket_x"] = 0
            screen.blit(collision, (dictionary["whole_session_data"]["second_monitor_width"] // settings.COLLISION_DIVISORS[0] - collision.get_width() // settings.COLLISION_DIVISORS[1], dictionary["whole_session_data"]["second_monitor_height"] // settings.COLLISION_DIVISORS[2] - collision.get_height() // settings.COLLISION_DIVISORS[3]))

    screen.blit(portal_image, (portal_x, portal_y))

    pygame.display.flip()

    return dictionary

def show_fixation_cross(dictionary: dict, screen: pygame.Surface):
    fixation: pygame.Surface = pygame.image.load(settings.FIXATION_PATH)

    screen.fill((0, 0, 0))  # fill the screen black

    new_width_fixation: float = settings.FIXATION_WIDTH
    new_height_fixation: float = settings.FIXATION_HEIGHT
    fix_resized: pygame.Surface = pygame.transform.scale(fixation, (new_width_fixation, new_height_fixation))
    fixation_width: float = fix_resized.get_width()
    fixation_height: float = fix_resized.get_height()
    dictionary["whole_session_data"]["fixation_width"]: float = fixation_width
    dictionary["whole_session_data"]["fixation_height"]: float = fixation_height

    screen.blit(fix_resized, (settings.SECOND_MONITOR_WIDTH // settings.FIX_LOCATION_SECMON_WIDTH_DIVISOR -
                              fixation_width // settings.FIX_LOCATION_WIDTH_DIVISOR,
                              settings.SECOND_MONITOR_HEIGHT // settings.FIX_LOCATION_SECMON_HEIGHT_DIVISOR -
                              fixation_height // settings.FIX_LOCATION_WIDTH_DIVISOR))  # show fixation cross

    pygame.display.flip()  # flip to monitor

def show_fixation_cross_rest(dictionary: dict, screen: pygame.Surface, Get_CSV_if_Error: bool):
    Logger.print_and_log(f"Showing {settings.REST_DURATION}s Rest")
    Logger.print_and_log("To Quit During Rest, type 'q'.")
    fixation_cross = pygame.image.load(settings.FIXATION_PATH)
    new_width_fixation: float = settings.FIXATION_WIDTH
    new_height_fixation: float = settings.FIXATION_HEIGHT
    fixation_cross = pygame.transform.scale(fixation_cross, (new_width_fixation, new_height_fixation))
    screen_width, screen_height = screen.get_size()
    fix_rect = fixation_cross.get_rect()
    fix_rect.center = (screen_width // settings.FIX_RECT_REST_DIVISORS[0], screen_height // settings.FIX_RECT_REST_DIVISORS[1])
    end_time = time.time() + settings.REST_DURATION

    # Display the fixation cross image for the specified duration
    while time.time() < end_time:
        # Check for events (including keypresses)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                Logger.print_and_log("Quit During Rest Block ... ")
                if Get_CSV_if_Error:
                    csv_log: str = Logger.create_log(filetype=".csv", log_name=f"{dictionary['whole_session_data']['pid']}_rifg_task")
                    Logger.update_log(log_name=csv_log, dictionary_to_write=dictionary)

                raise KeyboardInterrupt

        # Fill the screen with black
        screen.fill((0, 0, 0))

        # Blit (copy) the resized fixation cross image to the center of the screen
        screen.blit(fixation_cross, fix_rect)

        # Update the display to reflect the changes
        pygame.display.flip()
