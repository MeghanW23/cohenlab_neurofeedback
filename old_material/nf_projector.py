import subprocess
import pygame
import sys
import numpy as np
import json
import os
import time
from datetime import datetime
import math
import shutil
# from numba import jit

# Initialize Pygame
pygame.init()

# Mac Screen Info
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
print(f"Mac Screen Width: {SCREEN_WIDTH}")
print(f"Mac Screen Height: {SCREEN_HEIGHT}")

os.environ['SDL_VIDEO_WINDOW_POS'] = f'{SCREEN_WIDTH}, 0'

# Get information about all monitors
all_monitors = pygame.display.list_modes()

# Assuming you want to display on the second monitor
# If you have only one monitor or your second monitor is to the right of the primary one,
# you might need to adjust these values accordingly

second_monitor_index = 1

# Get the width and height of the second monitor
second_monitor_width, second_monitor_height = all_monitors[second_monitor_index]

# Set screen dimensions
screen = pygame.display.set_mode((second_monitor_width, second_monitor_height), pygame.NOFRAME)

"""
# Default screen dimensions if no second monitor is detected
DEFAULT_SCREEN_WIDTH = 800
DEFAULT_SCREEN_HEIGHT = 600

# Mac Screen Info
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
print(f"Mac Screen Width: {SCREEN_WIDTH}")
print(f"Mac Screen Height: {SCREEN_HEIGHT}")

# Check if a second monitor is available
all_monitors = pygame.display.list_modes()
if len(all_monitors) > 1:
    second_monitor_index = 1  # Assuming second monitor is connected
    second_monitor_width, second_monitor_height = all_monitors[second_monitor_index]
else:
    # No second monitor detected, use default dimensions
    second_monitor_width, second_monitor_height = DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT

# Set screen dimensions
screen = pygame.display.set_mode((second_monitor_width, second_monitor_height), pygame.NOFRAME)

# Center the window on the primary monitor
os.environ['SDL_VIDEO_WINDOW_POS'] = f'{SCREEN_WIDTH // 2 - second_monitor_width // 2}, {SCREEN_HEIGHT // 2 - second_monitor_height // 2}'
"""

print("Starting Neurofeedback Now")
pid = input("Enter Participant ID: ")
run = int(input("Enter Run Number: "))
block = int(input("Enter Block Number: "))
session = input("Enter Session Number: ")
start_timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

newParentDir = f"/Users/meghan/rt-cloud/nf_runs/{pid}_S{session}_{start_timestamp}"
os.makedirs(newParentDir)

# Set colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Writing
font = pygame.font.Font('/Users/meghan/neurofeedback/Space_Grotesk/SpaceGrotesk-VariableFont_wght.ttf', 36)

# Load the ball image
ball_image = pygame.image.load("/Users/meghan/neurofeedback/rocket.png")
ball_image_flames = pygame.image.load("/Users/meghan/neurofeedback/RocketwithFlames.png")


# change ball image size
ball_width = 250  # pixels
ball_height = 250  # height
ball_image = pygame.transform.scale(ball_image, (ball_width, ball_height))

# I calculated that the flames make the ball 32.08% longer, so allocate 32.08% more pixels on the width dimension (height is the same though)
ball_flames_width = ball_width * 1.3208  # pixels
ball_image_flames = pygame.transform.scale(ball_image_flames, (ball_flames_width, ball_height))

# Set initial position of the ball
initial_ball_x = second_monitor_width // 2 - ball_width // 2
ball_y = SCREEN_HEIGHT // 2 - ball_height // 2
print(f"Initial Ball Location: {initial_ball_x}, {ball_y}")

# Load the portal Image
portal_image = pygame.image.load("/Users/meghan/neurofeedback/portal.png")

# collision = font.render(f"Collision! Great Job!", True, (255, 255, 255))

collision = pygame.image.load("/Users/meghan/neurofeedback/CollisionWordArt.png")
collision_width = 500  # pixels
collision_height = 100  # height
collision = pygame.transform.scale(collision, (collision_width, collision_height))

streak = pygame.image.load("/Users/meghan/neurofeedback/highPerfText.png")
streak_width = 1000  # pixels
streak_height = 250  # height
streak = pygame.transform.scale(streak, (streak_width, streak_height))

# computer print bg
print_bg = pygame.image.load("/Users/meghan/neurofeedback/scifi_term.png")


""" DEFINE FUNCTIONS """
def error_notif(e):
    print("===========================================================================================================")
    print("=================================================ATTENTION=================================================")
    print(e)
    print("=================================================ATTENTION================================================")
    print("===========================================================================================================")

    # logging.info(f"====== ATTENTION ======")
    # logging.info(e)
    subprocess.run(['afplay', '/Users/meghan/neurofeedback/very_short_notif.mp3'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def get_progress(run, block):
    CalcBlock = 0
    if run == 1:
        if block == 1:
            CalcBlock = 1
        if block == 2:
            CalcBlock = 2
    elif run == 2:
        if block == 1:
            CalcBlock = 3
        if block == 2:
            CalcBlock = 4
    elif run == 3:
        if block == 1:
            CalcBlock = 5
        if block == 2:
            CalcBlock = 6
    progress = int((CalcBlock/6)*100)
    return progress, CalcBlock

def get_value_from_file(filename, backup):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError as e:    # if there are errors in the json file, use the 2nd to last as a backup
        print(f"JSON decoding error occurred for file '{filename}': {e}")
        print("Using Backup File ...")
        error_notif(e)
        try:
            with open(backup, 'r') as backup_file:
                data = json.load(backup_file)
        except Exception as backup_error:
            print(f"Failed to load backup file '{backup}': {backup_error}")
            error_notif(e)
            print("Backup FAILED, RETURNING 0 as VALUE")
            roi_value = 0.0
            return roi_value  # Return None if both files fail to load
        # Process the loaded JSON data
    roi_value = np.round(float(data['values']), 3)
    if roi_value != float(roi_value):
        if TR == 20 or TR == '20':
            print("NF SCORE IS INVALID. THIS IS EXPECTED AT TR20.")
            print("RETURNING 0 as VALUE")
            roi_value = 0.0
            return roi_value
        else:
            error_notif(e="NF SCORE IS INVALID")
            print("RETURNING 0 as VALUE")

            roi_value = 0.0
            return roi_value
    else:
        print(f"NF SCORE: {roi_value}")
    return roi_value

def calc_new_block_num(runOld, blockOld):   # calculate which run and block comes next
    runNew = 0
    blockNew = 0
    if runOld == 1 and blockOld == 1:
        runNew = 1
        blockNew = 2

    if runOld == 1 and blockOld == 2:
        runNew = 2
        blockNew = 1

    if runOld == 2 and blockOld == 1:
        runNew = 2
        blockNew = 2

    if runOld == 2 and blockOld == 2:
        runNew = 3
        blockNew = 1

    if runOld == 3 and blockOld == 1:
        runNew = 3
        blockNew = 2

    if runOld == 3 and blockOld == 2:
        print("ENDING LAST RUN AND BLOCK...")
        runNew = 100
        blockNew = 100

    return runNew, blockNew


def get_latest_json(directory):
    # List comprehension to get all files in the directory that end with '.dcm'
    json_files = [os.path.join(directory, file) for file in os.listdir(directory) if
                 os.path.isfile(os.path.join(directory, file)) and file.endswith('.json')]

    if not json_files:
        return None

    # Return the latest modified .dcm file
    return max(json_files, key=os.path.getmtime)


static_run_num = 1  # because the input json file never changes past 1 ...
startNew = 'y'
start_loop_time = ""
while startNew == 'y':
    level = 1
    portal = '100%'
    nf_score_list = []
    valueStreakCount = []
    # Create Background
    bg = pygame.image.load("/Users/meghan/neurofeedback/background426.png").convert()  # Replace "background.jpg" with your image file
    bg4 = pygame.image.load("/Users/meghan/neurofeedback/background4294.jpg").convert()
    bg2 = pygame.image.load("/Users/meghan/neurofeedback/background4293.png").convert()
    bg3 = pygame.image.load("/Users/meghan/neurofeedback/background4296.png").convert()

    bg = pygame.transform.scale(bg, (second_monitor_width, second_monitor_height))  # Scale the background image to match screen dimensions
    bg2 = pygame.transform.scale(bg2, (second_monitor_width, second_monitor_height))  # Scale the background image to match screen dimensions
    bg3 = pygame.transform.scale(bg3, (second_monitor_width, second_monitor_height))  # Scale the background image to match screen dimensions
    bg4 = pygame.transform.scale(bg4, (second_monitor_width, second_monitor_height))  # Scale the background image to match screen dimensions

    # Initial portal size
    portal_width = 500
    portal_height = 600
    portal_image = pygame.transform.scale(portal_image, (portal_width, portal_height))

    # Set initial position of the portal
    portal_x = second_monitor_width // 1.2 - portal_width // 2
    portal_y = SCREEN_HEIGHT // 2 - portal_height // 2

    # Initialize variables and paths for each run
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    outPath = "/Users/meghan/rt-cloud/outDir"
    ball_x = initial_ball_x
    radius = 100  # initial hoop size (if circle is used)
    collision_count = 0
    cross_width = 40  # Define fixation cross parameters
    cross_thickness = 4  # Define fixation cross parameters
    TR = 1  # resets to zero after starting a new block
    jsonDirList = 0  # Initialize count of JSON files in dir

    try:
        if run > 3 or block > 2:
            print("Finished all Runs and Blocks. Proceeding to Exit Screen")
            break
        print(f"Run Number is {run}")
        print(f"Block Number is {block}")
        # Prompt the user whether to start a new neurofeedback run
        if os.path.exists('/Users/meghan/rt-cloud/outDir'):
            os.rmdir('/Users/meghan/rt-cloud/outDir')
            print("Removed Old Outdir, Creating New One")

        subprocess.run(['mkdir', '/Users/meghan/rt-cloud/outDir'])
        print("Made the outDir")
        print("READY TO RECEIVE JSON FILES...")
    except Exception as e:
        error_notif(e)
        print("Issues with Starting New Script.")

    # Initialize While-Loop Dependent Variables
    currFilename = f"/Users/meghan/rt-cloud/outDir/rest_tr_{TR}.json"  # currFilename starts out using rest syntax, and then is changed to nf syntax later
    newPathFileName = f"{pid}_run{run}_block{block}_{timestamp}"
    newPath = os.path.join(newParentDir, newPathFileName)

    # Render Words
    progress, calc_block = get_progress(run=run, block=block)
    start_screen = font.render(f"Neurofeedback Block {calc_block} of 6. Please Try to get the Target into the Circle. Please Wait ...", True, (255, 255, 255))  # Text, antialiasing, color
    # calculate the progress for the progress screen
    progress_bar = font.render(f"Great Job! You are {progress}% done! Please Wait For Next Steps ...", True, (255, 255, 255))  # Text, antialiasing, color
    print_level = font.render(f"Level: {level}, Portals Reached: {collision_count}", True, (255, 255, 255))  # Text, antialiasing, color
    print_width, print_height = print_level.get_size()
    print_bg = pygame.transform.scale(print_bg, (print_width * 2, print_height * 2))

    # background must be blit before print
    screen.blit(print_bg, (
    second_monitor_width // 2.2 - print_bg.get_width() // 2, SCREEN_HEIGHT // 3 - print_bg.get_height() // 2))
    screen.blit(print_level, (
    second_monitor_width // 2.2 - print_level.get_width() // 2, SCREEN_HEIGHT // 3 - print_level.get_height() // 2))

    # START SCREEN
    while True:
        if os.path.exists(currFilename):
            print("Found the First File, Exiting the Start Screen")
            jsonDirList = len(os.listdir("/Users/meghan/rt-cloud/outDir/"))
            break
        else:
            screen.fill(BLACK)
            screen.blit(start_screen, (second_monitor_width // 2.2 - start_screen.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            time.sleep(0.1)
    # REST LOOP
    print("About to Start the Rest Loop")
    while TR < 20:
        start_loop_time = datetime.now()

        currFilename = f"/Users/meghan/rt-cloud/outDir/rest_tr_{TR}.json"
        if os.path.exists(currFilename) or len(os.listdir("/Users/meghan/rt-cloud/outDir/")) > jsonDirList:  # Either detect a new JSON with the expected TR in the filename, or detect that a new file or file(s) have been added to the directory
            print(f"=============TR{TR}============")
            print(f"RECEIVED REST TR{TR} JSON file")
            print("============================")

            # if the expected TR json file isn't the json that just entered the directory, get the newest json and make it currFilename to use in analysis
            if not os.path.exists(currFilename):
                print("Did Not Get Expected Dicom ...")
                currFilename = get_latest_json("/Users/meghan/rt-cloud/outDir/")
                print(f"Using Most Recent JSON File: {currFilename}")
            else:
                print(f"Using JSON File: {os.path.basename(currFilename)}")

            jsonDirList = len(os.listdir("/Users/meghan/rt-cloud/outDir/"))  # update list of JSON files

            end_loop_time = datetime.now()
            total_loop_time = end_loop_time - start_loop_time
            if total_loop_time.total_seconds() > 1.06:
                error_notif(e="CAUTION: THIS LOOP'S PROCESS TIME WAS GREATER THAN THE REPETITION TIME")
                print("=======================================================")
                print("CAUTION: THIS LOOP'S PROCESS TIME WAS GREATER THAN THE REPETITION TIME")
                print(f"Total Time: {total_loop_time}")
                print("=======================================================")
            elif total_loop_time.total_seconds() < 1.06:
                print(f"Loop Time: {total_loop_time}")

            TR += 1
        else:
            print("Waiting for next file.")
            # Fill the screen with black color
            screen.fill(BLACK)
            # Draw the vertical line of the fixation cross
            pygame.draw.line(screen, WHITE, (second_monitor_width // 2.2, SCREEN_HEIGHT // 2 - cross_width // 2), (second_monitor_width // 2.2, SCREEN_HEIGHT // 2 + cross_width // 2), cross_thickness)
            # Draw the horizontal line of the fixation cross
            pygame.draw.line(screen, WHITE, (second_monitor_width // 2.2 - cross_width // 2, SCREEN_HEIGHT // 2), (second_monitor_width // 2.2 + cross_width // 2, SCREEN_HEIGHT // 2), cross_thickness)
            # Update the display
            pygame.display.flip()
            # Check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            time.sleep(0.1)  # Adjust the sleep time as needed

    # NF LOOP
    while True:
        start_loop_time = datetime.now()

        currFilename = f"/Users/meghan/rt-cloud/outDir/run{static_run_num}_TR{TR}.json"
        backupFilename = f"/Users/meghan/rt-cloud/outDir/run{static_run_num}_TR{TR - 1}.json"
        lastFilename = f"/Users/meghan/rt-cloud/outDir/run{static_run_num}_TR140.json"

        if os.path.exists(currFilename) or len(os.listdir("/Users/meghan/rt-cloud/outDir/")) > jsonDirList:  # Either detect a new JSON with the expected TR in the filename, or detect that a new file or file(s) have been added to the directory
            print(f"=================================TR{TR}=====================================")
            print(f"RECEIVED JSON FILE FOR: NEUROFEEDBACK RUN{run}, BLOCK{block}, TR{TR} ")
            print("==========================================================================")

            # if the expected TR json file isn't the json that just entered the directory, get the newest json and make it currFilename to use in analysis
            if not os.path.exists(currFilename):
                print("Did Not Get Expected Dicom ...")
                currFilename = get_latest_json("/Users/meghan/rt-cloud/outDir/")
                print(f"Using Most Recent JSON File: {currFilename}")

            else:
                print(f"Using JSON File: {os.path.basename(currFilename)}")

            jsonDirList = len(os.listdir("/Users/meghan/rt-cloud/outDir/"))  # update list of JSON files

            # get NF value
            value = get_value_from_file(filename=currFilename, backup=backupFilename)

            try:
                # ball_x = ball_x + (value * 200)
                portal_range = range(0, int(portal_x))
                ball_x = (value + 1) * (len(portal_range) - 1) / 2
            except ValueError as e:
                error_notif(e)
                print(f"ATTENTION: THIS TRs VALUE: {value} CAUSED A VALUE ERROR. ")
                print("SKIPPING TR")

            # Limit the ball's movement to the screen bounds
            ball_x = max(0, ball_x)
            # print(f"Ball is at location: {ball_x} out of distance: {portal_x} ")
            print(f"{int((ball_x/portal_x)*100)}% of the Distance to the Portal")

            # Background Image:
            print(f"SUBJECT IS AT LEVEL #{level}")
            if level <= 1:
                screen.blit(bg, (0, 0))
            elif level == 2:
                screen.blit(bg2, (0, 0))
            elif level == 3:
                screen.blit(bg3, (0, 0))
            else:
                screen.blit(bg4, (0, 0))

            # Level Words
            print_level = font.render(f"Level: {level}, Portals Reached: {collision_count}", True, (255, 255, 255))  # Text, antialiasing, color
            print_width, print_height = print_level.get_size()
            print_bg = pygame.transform.scale(print_bg, (print_width * 2, print_height * 2))

            # background must be blit before print
            screen.blit(print_bg, (second_monitor_width // 2.2 - print_bg.get_width() // 2, SCREEN_HEIGHT // 3 - print_bg.get_height() // 2))
            screen.blit(print_level, (second_monitor_width // 2.2 - print_level.get_width() // 2, SCREEN_HEIGHT // 3 - print_level.get_height() // 2))

            if ball_x >= (portal_x * 0.9):
                screen.blit(collision, (second_monitor_width // 2.2 - collision.get_width() // 2, SCREEN_HEIGHT // 2 - collision.get_height() // 2))

            # blit the portal
            screen.blit(portal_image, (portal_x, portal_y))

            # blit the ball
            # If the user improve for 3 or more TRs consecutively, it shows the flames

            valueStreakCount.append(value)
            if len(valueStreakCount) > 1:
                if value >= valueStreakCount[-2]:
                    if len(valueStreakCount) >= 3:
                        screen.blit(ball_image_flames, (ball_x, ball_y))
                        screen.blit(streak, (second_monitor_width // 2.2 - streak.get_width() // 2,
                                             SCREEN_HEIGHT // 4 - streak.get_height() // 2))
                        print("==========================")
                        print("PARTICIPANT IS ON A STREAK")
                        print("==========================")
                    else:
                        screen.blit(ball_image, (ball_x, ball_y))
                else:
                    screen.blit(ball_image, (ball_x, ball_y))
                    valueStreakCount = []
            else:
                screen.blit(ball_image, (ball_x, ball_y))

            """
            if value >= 0:
                valueStreakCount.append(value)
                if len(valueStreakCount) >= 5:
                    screen.blit(ball_image_flames, (ball_x, ball_y))
                    screen.blit(streak, (second_monitor_width // 2.2 - streak.get_width() // 2,
                                            SCREEN_HEIGHT // 4 - streak.get_height() // 2))
                    print("=================")
                    print("ON A STREAK")
                    print("=================")


                else:
                    screen.blit(ball_image, (ball_x, ball_y))
            else:
                screen.blit(ball_image, (ball_x, ball_y))
                valueStreakCount = []
            """
            if ball_x >= (portal_x * 0.9):
                collision_count += 1
                ball_x = 0  # Resetting ball position

                if collision_count == 5:
                    # Shrink by 10%
                    shrink_percentage = 0.9
                    portal_width *= shrink_percentage
                    portal_height *= shrink_percentage

                    # Adjust the portal position to keep its center stationary
                    portal_x += ((portal_width * 0.1) / 2) + 25  # Adjust x by 5% of the width, then shift 25 pixels right
                    portal_y += (portal_height * 0.1) / 2  # Adjust y by 5% of the height

                    # Scale the portal image with the new dimensions
                    portal_image = pygame.transform.scale(portal_image, (int(portal_width), int(portal_height)))

                    print("============================")
                    print("============================")
                    print("THE CIRCLE HAS SHRUNK BY 10%")
                    print("============================")
                    print("============================")

                    level = 2
                    portal = '90%'

                if collision_count == 10:
                    # Shrink by 25%
                    shrink_percentage = 0.75
                    portal_width *= shrink_percentage
                    portal_height *= shrink_percentage

                    # Adjust the portal position to keep its center stationary
                    portal_x += ((portal_width * 0.25) / 2) + 50  # Adjust x by 12.5% of the width
                    portal_y += (portal_height * 0.25) / 2  # Adjust y by 12.5% of the height

                    # Scale the portal image with the new dimensions
                    portal_image = pygame.transform.scale(portal_image, (int(portal_width), int(portal_height)))
                    print("============================")
                    print("============================")
                    print("THE CIRCLE HAS SHRUNK BY 25%")
                    print("============================")
                    print("============================")

                    level = 3
                    portal = '75%'

                if collision_count == 20:
                    # Shrink by 50%
                    shrink_percentage = 0.5
                    portal_width *= shrink_percentage
                    portal_height *= shrink_percentage

                    # Adjust the portal position to keep its center stationary
                    portal_x += ((portal_width * 0.5) / 2) + 110  # Adjust x by 25% of the width, then adjust for the move left by moving pixels to the right
                    portal_y += (portal_height * 0.5) / 2  # Adjust y by 25% of the height

                    # Scale the portal image with the new dimensions
                    portal_image = pygame.transform.scale(portal_image, (int(portal_width), int(portal_height)))

                    print("============================")
                    print("============================")
                    print("THE CIRCLE HAS SHRUNK BY 50%")
                    print("============================")
                    print("============================")

                    level = 4
                    portal = '50%'

                print("==============COLLISION==============")
                print(f"Collision Number {collision_count}")
                print(f"Portal Width: {portal_width}")
                print(f"Portal Height: {portal_height}")
                print("==============COLLISION==============")

                # Calculate the y-coordinate of the ball relative to the center of the portal
                ball_y = portal_y + (portal_height // 2) - (ball_height // 2)

            # Update the display
            pygame.display.flip()
            # Add a small delay to control frame rate
            # pygame.time.delay(1060)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            end_loop_time = datetime.now()
            total_loop_time = end_loop_time - start_loop_time
            if total_loop_time.total_seconds() > 1.06:
                error_notif(e="CAUTION: THIS LOOP'S PROCESS TIME WAS GREATER THAN THE REPETITION TIME")
                print("=======================================================")
                print("CAUTION: THIS LOOP'S PROCESS TIME WAS GREATER THAN THE REPETITION TIME")
                print(f"Total Time: {total_loop_time}")
                print("=======================================================")
            elif total_loop_time.total_seconds() < 1.06:
                print(f"Loop Time: {total_loop_time}")

            TR += 1

            if currFilename == lastFilename:
                print(f"THIS IS THE LAST TR of RUN {run}, BLOCK {block}, WITH SUBJECT {pid}")
                # Move contents of outPath to newPath
                shutil.move(outPath, newPath)
                print(f"RUN JSON FILES MOVED TO: {newPath}")

                if block == 2:
                    print("THIS IS BLOCK 2, SO THERE ARE AN EXTRA 20 TRS REST AT THE END")
                    screen.fill(BLACK)
                    # Draw the vertical line of the fixation cross
                    pygame.draw.line(screen, WHITE, (second_monitor_width // 2.2, SCREEN_HEIGHT // 2 - cross_width // 2),
                                     (second_monitor_width // 2.2, SCREEN_HEIGHT // 2 + cross_width // 2), cross_thickness)
                    # Draw the horizontal line of the fixation cross
                    pygame.draw.line(screen, WHITE, (second_monitor_width // 2.2 - cross_width // 2, SCREEN_HEIGHT // 2),
                                     (second_monitor_width // 2.2 + cross_width // 2, SCREEN_HEIGHT // 2), cross_thickness)
                    # Update the display
                    pygame.display.flip()
                    rest_20trs = 1.06 * 20
                    time.sleep(rest_20trs)
                    # Check for events
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()

                # Blit the Ending Progress Report
                screen.fill(BLACK)
                screen.blit(progress_bar, (second_monitor_width // 2.2 - progress_bar.get_width() // 2, SCREEN_HEIGHT // 2 - progress_bar.get_height() // 2))
                pygame.display.flip()
                time.sleep(3)
                print("Printing the Ending Progress Report for 5 seconds ...")

                # Clear out the outDir by removing it entirely.
                subprocess.run(['rm', '-rf', '/Users/meghan/rt-cloud/outDir'])
                print(f"Removed the outPath folder")

                # if run and block come out to greater than 3 and 2 , respectively, the while loop breaks
                run, block = calc_new_block_num(runOld=run, blockOld=block)
                break  # Breaks the Inner While Loop (doesn't stop whole loop)

        else:
            time.sleep(0.1)


# Exit Screen
screen.fill(BLACK)
exit_screen = font.render(f" All Done! Please Wait For Experimenter ...", True, (255, 255, 255))  # Text, antialiasing, color
screen.blit(exit_screen, (second_monitor_width // 2.2 - exit_screen.get_width() // 2, SCREEN_HEIGHT // 2 - exit_screen.get_height() // 2))
pygame.display.flip()
print("ALL DONE - DISPLAYING GOODBYE SCREEN FOR 5 MINUTES...")
time.sleep(300)
