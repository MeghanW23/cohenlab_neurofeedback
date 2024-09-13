import pygame
import random
import csv
import os
import Projector
import Logger
import settings
import ScriptManager
# set a fixed seed for reproducibility of a pseudorandom series
random.seed(settings.RANDOM_SEED_VALUE)
pid = ScriptManager.get_participant_id()
output_log_path = Logger.create_log(filetype=".txt", log_name=f"{pid}_MSIT")

""" FUNCTIONS """
def generate_series():
    series_list = []

    for i in range(10):
        same_number = random.randint(1, 9)

        different_number = same_number
        while different_number == same_number:
            different_number = random.randint(1, 9)

        positions = [0, 1, 2]  # Positions 0, 1, and 2
        random.shuffle(positions)  # Shuffle positions to decide where the different number will go

        series = [same_number, same_number, same_number]
        series[positions[0]] = different_number  # Assign different number to random position

        series_list.append(series)

    return series_list


def get_response():
    response = None
    start_time = pygame.time.get_ticks()
    while response is None:
        current_time = pygame.time.get_ticks()
        if current_time - start_time > 3000:  # Timeout after 3 seconds
            return None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Key presses mapped to positions
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:  # 'A' key is position 0
                    response = 0
                elif event.key == pygame.K_b:  # 'B' key is position 1
                    response = 1
                elif event.key == pygame.K_c:  # 'C' key is position 2
                    response = 2
    return response


def display_message(message, duration=2000):
    screen.fill(white)
    text_surface = font.render(message, True, black)
    screen.blit(text_surface, (300, 200))  # Display above the number series
    pygame.display.flip()
    pygame.time.wait(duration)


def save_to_csv(data, participant_id):
    # Ensure the directory exists
    if not os.path.exists(settings.MSIT_LOG_DIR):
        os.makedirs(settings.MSIT_LOG_DIR)

    # Define the full path to the CSV file
    file_path = os.path.join(settings.MSIT_LOG_DIR, f"participant_{participant_id}_msit_results.csv")

    # Save the data to the CSV file
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Trial Number", "Participant ID", "Key Pressed"])
        writer.writerows(data)


pygame.init()

info = pygame.display.Info()

# Select the second display (if available)
if pygame.display.get_num_displays() > 1:
    screen = pygame.display.set_mode((800, 600), display=1)  # Use second monitor
else:
    screen = pygame.display.set_mode((800, 600))  # Use primary monitor

pygame.display.set_caption("MSIT Task")
font = pygame.font.Font(None, 74)

white = (255, 255, 255)
black = (0, 0, 0)


# Run the experiment
def run_experiment(participant_id):
    dictionary = {
        "whole_session_data": {
            "pid": participant_id
        }
    }

    # Display instructions
    display_message(
        "Welcome to the MSIT Task! "
        "Please indicate in which position the number that's different from the others is in."
        "If it's on the left, press A using your left thumb. "
        "If it's in the middle, press B using your left index finger."
        "If it's on the right, press C using your right index finger."
        "If you miss one, don't worry, just keep going!"
        "When the Fixation Cross (+) appears, please look directly at it.")

    Projector.show_fixation_cross_rest(dictionary=dictionary, screen=screen, Get_CSV_if_Error=False)  # 30 sec rest period before experiment begins

    series_list = generate_series()
    trial_data = []  # list to store data for CSV

    # Loop over the 10 series - can be adjusted to whatever we want later
    for i, series in enumerate(series_list):
        screen.fill(white)

        # Display the current series on the screen
        numbers_text = f"{series[0]}  {series[1]}  {series[2]}"
        text_surface = font.render(numbers_text, True, black)
        screen.blit(text_surface, (300, 250))

        pygame.display.flip()

        start_time = pygame.time.get_ticks()

        # display the series for 3 seconds
        response = None
        while pygame.time.get_ticks() - start_time < 3000:  # loop for 3 seconds
            response = get_response()
            if response is not None:
                break

        # Display which key was pressed
        if response is not None:
            key_pressed = {0: 'A', 1: 'B', 2: 'C'}[response]
            display_message(f"Pressed {key_pressed}", duration=2000)
        else:
            display_message("No response", duration=2000)  # Handle case where no key was pressed

        # Store trial data (trial number, participant ID, key pressed or "No response")
        if response is not None:
            key_pressed = {0: 'A', 1: 'B', 2: 'C'}[response]
            trial_data.append([i + 1, participant_id, key_pressed])
        else:
            trial_data.append([i + 1, participant_id, "No response"])

        # Pause for a moment between series
        pygame.time.wait(1000)

    Projector.show_fixation_cross_rest(dictionary=dictionary, screen=screen, Get_CSV_if_Error=False)  # 30 sec rest period showing fixation cross before end message

    display_message("Task Complete! Thank you for participating.", duration=3000)

    # Save the trial data to CSV after the experiment is complete
    save_to_csv(trial_data, participant_id)

    pygame.quit()

"""" RUN EXPERIMENT """

participant_id = input("Enter participant ID: ")

run_experiment(participant_id)

