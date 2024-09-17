import sys
import pygame
from typing import Tuple
import os
import time
import Logger
import settings
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
    Logger.print_and_log("Showing Instructions. Task will start when 's' is pressed.")
    font: pygame.font.Font = pygame.font.Font(None, settings.INSTRUCT_MESSAGE_FONT_SIZE)
    # Clear the screen
    screen.fill((0, 0, 0))

    y_offset = settings.INSTRUCT_Y_OFFSET  # Start y-position
    for line in instructions:
        text: pygame.Surface = font.render(line, True, settings.FONT_COLOR)  # White text
        text_rect: pygame.Rect = text.get_rect(center=(screen.get_width() // 2, y_offset))
        screen.blit(text, text_rect)
        y_offset += settings.INSTRUCT_Y_OFFSET_INCREMENT  # Increment y-position for each new line

    pygame.display.flip()

    # Wait for 's' key press to proceed
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                return
            pygame.time.wait(100)
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
def setup_nfb_icons(dictionary: dict) -> dict:
    dictionary["whole_session_data"]["portal_image"]: pygame.Surface = pygame.image.load(settings.PORTAL_PATH)
    dictionary["whole_session_data"]["portal_image"]: pygame.Surface = pygame.transform.scale(dictionary["whole_session_data"]["portal_image"], (settings.PORTAL_WIDTH, settings.PORTAL_HEIGHT))

    dictionary["whole_session_data"]["collision_image"]: pygame.Surface = pygame.image.load(settings.COLLISION_WORD_ART)
    dictionary["whole_session_data"]["collision_image"]: pygame.Surface = pygame.transform.scale(dictionary["whole_session_data"]["collision_image"], (settings.COLLISION_WIDTH, settings.COLLISION_HEIGHT))

    dictionary["whole_session_data"]["streak_image"]: pygame.Surface = pygame.image.load(settings.HIGH_PERFORM_WORD_ART)
    dictionary["whole_session_data"]["streak_image"]: pygame.Surface = pygame.transform.scale(dictionary["whole_session_data"]["streak_image"], (settings.STREAK_WIDTH, settings.STREAK_HEIGHT))

    dictionary["whole_session_data"]["print_bg"]: pygame.Surface = pygame.image.load(settings.PRINT_BACKGROUND)

    dictionary["whole_session_data"]["rocket_image"]: pygame.Surface = pygame.image.load(settings.ROCKET_PATH)
    dictionary["whole_session_data"]["rocket_image"]: pygame.Surface = pygame.transform.scale(dictionary["whole_session_data"]["rocket_image"], (settings.ROCKET_WIDTH, settings.ROCKET_HEIGHT))

    dictionary["whole_session_data"]["rocket_image_flames"]: pygame.Surface = pygame.image.load(settings.ROCKET_WITH_FLAMES_PATH)
    dictionary["whole_session_data"]["rocket_image_flames"]: pygame.Surface = pygame.transform.scale(dictionary["whole_session_data"]["rocket_image_flames"], (settings.ROCKET_FLAMES_WIDTH, settings.ROCKET_FLAMES_HEIGHT))

    # Set initial position of the rocket, portal
    dictionary["whole_session_data"]["initial_rocket_x"] = dictionary["whole_session_data"][
                                           "second_monitor_width"] // settings.INITIAL_ROCKET_LOCATION_SECMON_WIDTH_DIVISOR - settings.ROCKET_WIDTH // settings.ROCKET_WIDTH_LOCATION_DIVISOR
    dictionary["whole_session_data"]["rocket_y"] = dictionary["whole_session_data"][
                                   "second_monitor_height"] // settings.INITIAL_ROCKET_LOCATION_SECMON_HEIGHT_DIVISOR - settings.ROCKET_HEIGHT // settings.ROCKET_WIDTH_LOCATION_DIVISOR
    dictionary["whole_session_data"]["portal_x"] = dictionary["whole_session_data"][
                                   "second_monitor_width"] // settings.PORTAL_LOCATION_SECMON_WIDTH_DIVISOR - settings.PORTAL_WIDTH // settings.PORTAL_WIDTH_LOCATION_DIVISOR
    dictionary["whole_session_data"]["portal_y"] = dictionary["whole_session_data"][
                                   "second_monitor_height"] // settings.PORTAL_LOCATION_SECMON_HEIGHT_DIVISOR - settings.PORTAL_HEIGHT // settings.PORTAL_HEIGHT_LOCATION_DIVISOR

    dictionary["whole_session_data"]["bg"] = pygame.transform.scale(pygame.image.load(settings.BACKGROUND_PATH_1).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))
    dictionary["whole_session_data"]["bg2"] = pygame.transform.scale(pygame.image.load(settings.BACKGROUND_PATH_2).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))
    dictionary["whole_session_data"]["bg3"] = pygame.transform.scale(pygame.image.load(settings.BACKGROUND_PATH_3).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))
    dictionary["whole_session_data"]["bg4"] = pygame.transform.scale(pygame.image.load(settings.BACKGROUND_PATH_4).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))

    return dictionary
def check_nfb_block_setup(dictionary: dict, block: int, trial: int) -> Tuple[dict, str, str]:
    current_block: str = f"block{block}"
    current_trial: str = f"trial{trial}"
    if "current_level" not in dictionary[current_block]:
        dictionary[current_block]["current_level"]: int = 1
    if "collision_count" not in dictionary[current_block]:
        dictionary[current_block]["collision_count"]: int = 0
    if "portal_x" not in dictionary[current_block]:
        dictionary[current_block]["portal_x"] = dictionary["whole_session_data"]["portal_x"]
    if "portal_y" not in dictionary[current_block]:
        dictionary[current_block]["portal_y"] = dictionary["whole_session_data"]["portal_y"]
    if "portal_image" not in dictionary[current_block]:
        dictionary[current_block]["portal_image"] = dictionary["whole_session_data"]["portal_image"]

    return dictionary, current_block, current_trial
def nfb_collision_handler(dictionary: dict, current_block: str, screen: pygame.Surface) -> dict:
    if dictionary[current_block]["rocket_x"] >= (dictionary[current_block]["portal_x"] * 0.9):  # collision
        dictionary[current_block]["collision_count"] += 1
        dictionary[current_block]["rocket_x"] = 0
        screen.blit(dictionary["whole_session_data"]["collision_image"], (dictionary["whole_session_data"]["second_monitor_width"] // settings.COLLISION_DIVISORS[0] - dictionary["whole_session_data"]["collision_image"].get_width() // settings.COLLISION_DIVISORS[1], dictionary["whole_session_data"]["second_monitor_height"] // settings.COLLISION_DIVISORS[2] - dictionary["whole_session_data"]["collision_image"].get_height() // settings.COLLISION_DIVISORS[3]))

        portal_height = dictionary[current_block]["portal_image"].get_height()
        portal_width = dictionary[current_block]["portal_image"].get_width()

        if dictionary[current_block]["current_level"] == 1 and dictionary[current_block]["collision_count"] == settings.LEVEL_TWO_COLLISION_REQUIREMENTS:
            shrink_percentage = 0.9
            portal_width *= shrink_percentage
            portal_height *= shrink_percentage

            # Adjust the portal position to keep its center stationary
            dictionary[current_block]["portal_x"] += ((portal_width * 0.1) / 2) + settings.LEVEL_TWO_COLLISION_ADJUSTMENT_X  # Adjust x by 5% of the width, then shift 25 pixels right
            dictionary[current_block]["portal_y"] += ((portal_height * 0.1) / 2) + settings.LEVEL_TWO_COLLISION_ADJUSTMENT_Y  # Adjust y by 5% of the height

            dictionary[current_block]["portal_image"] = pygame.transform.scale(
                dictionary[current_block]["portal_image"], (int(portal_width), int(portal_height)))

            Logger.print_and_log("============================")
            Logger.print_and_log("THE CIRCLE HAS SHRUNK BY 10%")
            Logger.print_and_log("============================")

            dictionary[current_block]["current_level"] = 2


        elif dictionary[current_block]["current_level"] == 2 and dictionary[current_block]["collision_count"] == settings.LEVEL_THREE_COLLISION_REQUIREMENTS:
            shrink_percentage = 0.75
            portal_width *= shrink_percentage
            portal_height *= shrink_percentage

            # Adjust the portal position to keep its center stationary
            dictionary[current_block]["portal_x"] += ((portal_width * 0.1) / 2) + settings.LEVEL_THREE_COLLISION_ADJUSTMENT_X  # Adjust x by 5% of the width, then shift 25 pixels right
            dictionary[current_block]["portal_y"] += ((portal_height * 0.1) / 2) + settings.LEVEL_THREE_COLLISION_ADJUSTMENT_Y  # Adjust y by 5% of the height

            dictionary[current_block]["portal_image"] = pygame.transform.scale(dictionary[current_block]["portal_image"], (int(portal_width), int(portal_height)))

            Logger.print_and_log("============================")
            Logger.print_and_log("THE CIRCLE HAS SHRUNK BY 25%")
            Logger.print_and_log("============================")

            dictionary[current_block]["current_level"] = 3


        elif dictionary[current_block]["current_level"] == 3 and dictionary[current_block]["collision_count"] == settings.LEVEL_FOUR_COLLISION_REQUIREMENTS:
            shrink_percentage = 0.5
            portal_width *= shrink_percentage
            portal_height *= shrink_percentage

            # Adjust the portal position to keep its center stationary
            dictionary[current_block]["portal_x"] += ((portal_width * 0.1) / 2) + settings.LEVEL_FOUR_COLLISION_ADJUSTMENT_X  # Adjust x by 5% of the width, then shift 25 pixels right
            dictionary[current_block]["portal_y"] += ((portal_height * 0.1) / 2) + settings.LEVEL_FOUR_COLLISION_ADJUSTMENT_Y  # Adjust y by 5% of the height

            dictionary[current_block]["portal_image"] = pygame.transform.scale(dictionary[current_block]["portal_image"], (int(portal_width), int(portal_height)))

            Logger.print_and_log("============================")
            Logger.print_and_log("THE CIRCLE HAS SHRUNK BY 50%")
            Logger.print_and_log("============================")

            dictionary[current_block]["current_level"] = 4

    return dictionary
def nfb_streak_count(dictionary: dict, current_block: str, screen: pygame.Surface) -> Tuple[dict, bool]:
    streak: bool = False

    if "streak_counter" not in dictionary[current_block]:
        Logger.print_and_log("adding streak counter to block")
        dictionary[current_block]["streak_counter"]: int = 0
    if len(dictionary[current_block]["nf_scores"]) > 1:
        if dictionary[current_block]["nf_scores"][-2] < dictionary[current_block]["nf_scores"][-1]:
            dictionary[current_block]["streak_counter"] += 1
        else:
            dictionary[current_block]["streak_counter"] = 0

    if dictionary[current_block]["streak_counter"] >= settings.TRIALS_BEFORE_STREAK_REPORT:
        streak: bool = True
        screen.blit(dictionary["whole_session_data"]["streak_image"], (dictionary["whole_session_data"]["second_monitor_width"] // settings.STREAK_LOCATION_DIVISORS[0] - dictionary["whole_session_data"]["streak_image"].get_width() // settings.STREAK_LOCATION_DIVISORS[1],
                             dictionary["whole_session_data"]["second_monitor_height"] // settings.STREAK_LOCATION_DIVISORS[2] - dictionary["whole_session_data"]["streak_image"].get_height() // settings.STREAK_LOCATION_DIVISORS[3]))
        Logger.print_and_log("SUBJECT IS ON A STREAK")

    return dictionary, streak
def project_nfb_trial(dictionary: dict, screen: pygame.Surface, block: int, trial: int) -> dict:
    screen.fill((0, 0, 0))

    dictionary, current_block, current_trial = check_nfb_block_setup(dictionary=dictionary, block=block, trial=trial)

    Logger.print_and_log(f"Participant is at level #{dictionary[current_block]['current_level']}")
    if dictionary[current_block]["current_level"] <= 1:
        screen.blit(dictionary["whole_session_data"]["bg"], (0, 0))

    elif dictionary[current_block]["current_level"] == 2:
        screen.blit(dictionary["whole_session_data"]["bg2"], (0, 0))

    elif dictionary[current_block]["current_level"] == 3:
        screen.blit(dictionary["whole_session_data"]["bg3"], (0, 0))

    else:
        screen.blit(dictionary["whole_session_data"]["bg4"], (0, 0))

    # Level Words
    print_level = settings.FONT.render(f"Level: {dictionary[current_block]['current_level']}, Portals Reached: {dictionary[current_block]['collision_count']}", True, settings.FONT_COLOR)  # Text, antialiasing, color
    print_width, print_height = print_level.get_size()
    print_bg = pygame.transform.scale(dictionary["whole_session_data"]["print_bg"], (print_width * 2, print_height * 2))

    # background must be blit before print
    screen.blit(print_bg, (dictionary["whole_session_data"]["second_monitor_width"] // settings.PRINT_BG_LOCATION_DIVISORS[0] - print_bg.get_width() // settings.PRINT_BG_LOCATION_DIVISORS[1], dictionary["whole_session_data"]["second_monitor_height"] // settings.PRINT_BG_LOCATION_DIVISORS[2] - print_bg.get_height() // settings.PRINT_BG_LOCATION_DIVISORS[3]))
    screen.blit(print_level, (dictionary["whole_session_data"]["second_monitor_width"] // settings.PRINT_LEVEL_LOCATION_DIVISORS[0] - print_level.get_width() // settings.PRINT_LEVEL_LOCATION_DIVISORS[1], dictionary["whole_session_data"]["second_monitor_height"] // settings.PRINT_LEVEL_LOCATION_DIVISORS[2] - print_level.get_height() // settings.PRINT_LEVEL_LOCATION_DIVISORS[3]))
    screen.blit(dictionary[current_block]["portal_image"], (dictionary[current_block]["portal_x"], dictionary[current_block]["portal_y"]))

    nfb_type: str = ""
    if settings.NFB_FROM_MEAN_ACTIVATION:
        nfb_type: str = "normalized_mean_activation"

    elif settings.NFB_FROM_RESIDUAL_VALUE:
        nfb_type: str = "normalized_resid_mean"

    # add one to the value so the values are between (0, 2) and not (-1, 1)
    if settings.NFB_FROM_MEAN_ACTIVATION:
        nfb_value: float = dictionary[current_block][current_trial][nfb_type]

    elif settings.NFB_FROM_RESIDUAL_VALUE:
        nfb_value: float = dictionary[current_block][current_trial][nfb_type]
    else:
        Logger.print_and_log("Please Choose What Calculation You Want To Run via the settings script. ex: mean_activation, residuals, etc.")
        sys.exit(1)

    if current_trial == "trial1" or current_trial == "trial2" or current_trial == "trial3":
        Logger.print_and_log("Not Yet Showing Subject The Feedback (Too Early)")
        screen.blit(dictionary["whole_session_data"]["rocket_image"], (0, dictionary["whole_session_data"]["rocket_y"]))

    else:
        rocket_x = int((nfb_value + 1) / 2 * dictionary[current_block]["portal_x"])
        dictionary[current_block]["rocket_x"] = rocket_x

        Logger.print_and_log("========================================")
        Logger.print_and_log(f"{int((rocket_x / dictionary[current_block]['portal_x']) * 100)}% of the way to the portal. ")
        Logger.print_and_log("========================================")

        dictionary, streak = nfb_streak_count(dictionary=dictionary, current_block=current_block, screen=screen)
        if streak:
            screen.blit(dictionary["whole_session_data"]["rocket_image_flames"], (dictionary[current_block]["rocket_x"], dictionary["whole_session_data"]["rocket_y"]))
        else:
            screen.blit(dictionary["whole_session_data"]["rocket_image"], (rocket_x, dictionary["whole_session_data"]["rocket_y"]))
        dictionary = nfb_collision_handler(dictionary=dictionary, current_block=current_block, screen=screen)

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
def show_message(screen: pygame.Surface, message: list, wait_for_scanner: bool) -> None:
    Logger.print_and_log("Showing Inter-Trial Message.")
    font: pygame.font.Font = pygame.font.Font(None, settings.INSTRUCT_MESSAGE_FONT_SIZE)
    # Clear the screen
    screen.fill((0, 0, 0))

    y_offset = settings.INSTRUCT_Y_OFFSET  # Start y-position
    for line in message:
        text: pygame.Surface = font.render(line, True, settings.FONT_COLOR)  # White text
        text_rect: pygame.Rect = text.get_rect(center=(screen.get_width() // 2, y_offset))
        screen.blit(text, text_rect)
        y_offset += settings.INSTRUCT_Y_OFFSET_INCREMENT  # Increment y-position for each new line

    pygame.display.flip()

    if wait_for_scanner:
        # Wait for 's' key press to proceed
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    return
                pygame.time.wait(100)