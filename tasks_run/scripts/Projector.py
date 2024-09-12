import pygame
from typing import Tuple
import settings
import os
import time
import Logger

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

    # Create a Pygame display window on the second monitor
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
def setup_nfb_trial_projection(dictionary: dict):
    portal_image: pygame.Surface = pygame.image.load(settings.PORTAL_PATH)
    collision: pygame.Surface = pygame.image.load(settings.COLLISION_WORD_ART)
    streak: pygame.Surface = pygame.image.load(settings.HIGH_PERFORM_WORD_ART)
    print_bg: pygame.Surface = pygame.image.load(settings.PRINT_BACKGROUND)
    rocket_image: pygame.Surface = pygame.image.load(settings.ROCKET_PATH)
    rocket_image_flames: pygame.Surface = pygame.image.load(settings.ROCKET_WITH_FLAMES_PATH)

    rocket_image: pygame.Surface = pygame.transform.scale(rocket_image, (settings.rocket_width, settings.rocket_height))
    rocket_image_flames = pygame.transform.scale(rocket_image_flames,
                                                 (settings.rocket_flames_width, settings.rocket_flames_height))

    portal_image: pygame.Surface = pygame.transform.scale(portal_image, (settings.portal_width, settings.portal_height))

    # Set initial position of the ball
    initial_rocket_x = dictionary["whole_session_data"][
                           "second_monitor_width"] // settings.INITIAL_ROCKET_LOCATION_SECMON_WIDTH_DIVISOR - settings.rocket_width // settings.ROCKET_WIDTH_LOCATION_DIVISOR
    rocket_y = dictionary["whole_session_data"][
                   "second_monitor_height"] // settings.INITIAL_ROCKET_LOCATION_SECMON_HEIGHT_DIVISOR - settings.rocket_height // settings.ROCKET_WIDTH_LOCATION_DIVISOR

    bg = pygame.transform.scale(pygame.image.load(settings.BACKGROUND_PATH_1).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))
    bg2 = pygame.transform.scale(pygame.image.load(settings.BACKGROUND_PATH_2).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))
    bg3 = pygame.transform.scale(pygame.image.load(settings.BACKGROUND_PATH_3).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))
    bg4 = pygame.transform.scale(pygame.image.load(settings.BACKGROUND_PATH_4).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))

    portal_x = dictionary["whole_session_data"][
                   "second_monitor_width"] // settings.PORTAL_LOCATION_SECMON_WIDTH_DIVISOR - settings.portal_width // settings.PORTAL_WIDTH_LOCATION_DIVISOR
    portal_y = dictionary["whole_session_data"][
                   "second_monitor_height"] // settings.PORTAL_LOCATION_SECMON_HEIGHT_DIVISOR - settings.portal_height // settings.PORTAL_HEIGHT_LOCATION_DIVISOR

    rocket_x: float = initial_rocket_x

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


