import pandas as pd
import os
import re
import sys


sys.path.append("/workdir/tasks_run/scripts")
import settings
import FileHandler

def parse_msit_log(file_path):
    print(f"Parsing MSIT TXT log file: {file_path}")

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return pd.DataFrame()

    trials = []
    trial_pattern = re.compile(r'=======Trial (\d+), Block (\d+) =======')
    number_series_pattern = re.compile(r'Number Series: \[(\d+), (\d+), (\d+)]')
    response_pattern = re.compile(r'Response: ([A-C])/([1-3])')
    correct_pattern = re.compile(r'Response: Correct')
    no_response_pattern = re.compile(r'No Response For This Trial')
    incorrect_pattern = re.compile(r'== INCORRECT RESPONSE ==')

    with open(file_path, 'r') as file:
        lines = file.readlines()

    print(f"Total lines in file: {len(lines)}\n")

    # Print first 50 lines to verify file structure
    print("First 50 lines of the file:")
    for i, line in enumerate(lines[:50]):
        print(f"{i + 1}: {repr(line)}")

    # Find the first trial
    trial_start_idx = next((i for i, line in enumerate(lines) if trial_pattern.search(line)), None)

    if trial_start_idx is None:
        print("No trials detected! Check log file format.")
        return pd.DataFrame()

    print(f"First trial detected at line {trial_start_idx + 1}. Skipping metadata...\n")

    # Process only lines starting from the first trial
    lines = lines[trial_start_idx:]

    current_trial = {}
    for i, line in enumerate(lines):
        trial_match = trial_pattern.search(line)
        if trial_match:
            if current_trial:
                trials.append(current_trial)
            current_trial = {
                'trial': int(trial_match.group(1)),
                'block': int(trial_match.group(2)),
                'number_series': None,
                'response': None,
                'correct': None
            }
            print(f"Trial {trial_match.group(1)} detected at line {i + trial_start_idx + 1}.")
            continue

        number_series_match = number_series_pattern.search(line)
        if number_series_match:
            current_trial['number_series'] = [int(number_series_match.group(i)) for i in range(1, 4)]
            continue

        response_match = response_pattern.search(line)
        if response_match:
            current_trial['response'] = response_match.group(2)
            continue

        if correct_pattern.search(line):
            current_trial['correct'] = True
            continue

        if incorrect_pattern.search(line):
            current_trial['correct'] = False
            continue

        if no_response_pattern.search(line):
            current_trial['response'] = 'No Response'
            current_trial['correct'] = False
            continue

    if current_trial:
        trials.append(current_trial)

    df = pd.DataFrame(trials)

    if df.empty:
        print("Parsed DataFrame is empty! Check regex patterns or log file format.")

    print("Parsed MSIT DataFrame:")
    print(df.head(10))  # Show first 10 rows for verification

    return df

def parse_rifg_log(file_path):
    print("Parsing RIFG TXT log file...")

    trials = []
    trial_pattern = re.compile(r'^\s*====\s*Starting\s+Trial\s+(\d+)\s*====\s*$')
    stimulus_pattern = re.compile(r'Stimulus:\s*(\w+)')
    response_pattern = re.compile(r'Pressed (A|B|C)')
    result_pattern = re.compile(r'Result:\s*(.+)')

    with open(file_path, 'r') as file:
        lines = file.readlines()

    print(f"Total lines in file: {len(lines)}\n")

    # Find the first trial line
    trial_start_idx = next((i for i, line in enumerate(lines) if trial_pattern.search(line)), None)

    if trial_start_idx is None:
        print("No trials detected! Check log file format.")
        return pd.DataFrame()

    print(f"First trial detected at line {trial_start_idx + 1}. Skipping metadata...\n")

    # Only process lines starting from the first trial**
    lines = lines[trial_start_idx:]

    current_trial = {}
    for i, line in enumerate(lines):
        trial_match = trial_pattern.search(line)
        if trial_match:
            if current_trial:
                trials.append(current_trial)
            current_trial = {
                'trial': int(trial_match.group(1)),
                'stimulus': None,
                'pressed_a': False,
                'pressed_b': False,
                'pressed_c': False,
                'result': None
            }
            print(f"Trial {trial_match.group(1)} detected at line {i + trial_start_idx + 1}.")
            continue

        stimulus_match = stimulus_pattern.search(line)
        if stimulus_match:
            current_trial['stimulus'] = stimulus_match.group(1)
            continue

        response_match = response_pattern.search(line)
        if response_match:
            key_pressed = response_match.group(1)  # Captures 'A' or 'B'
            if key_pressed == "A":
                current_trial['pressed_a'] = True
            elif key_pressed == "B":
                current_trial['pressed_b'] = True
            elif key_pressed == "C":
                current_trial['pressed_c'] = True
            continue

        result_match = result_pattern.search(line)
        if result_match:
            current_trial['result'] = result_match.group(1).strip()
            continue

    if current_trial:
        trials.append(current_trial)

    df = pd.DataFrame(trials)

    if df.empty:
        print("Parsed DataFrame is empty! Check regex patterns or log file format.")

    print("Parsed RIFG DataFrame:")
    print(df.head(10))  # Show first 10 rows for verification

    return df

def analyze_rifg_responses(df, output_summary):
    print("Filtering false alarm and hit trials...")
    if 'result' not in df.columns:
        raise KeyError("Column 'result' is missing from parsed data. Check regex parsing.")

    filtered_df = df[df['result'].isin(['false_alarm', 'hit'])].copy()

    print("Checking previous trial result for false alarms...")
    filtered_df['previous_trial_result'] = df['result'].shift(1)

    print(f"Saving analyzed data to {output_summary}...")
    filtered_df.to_csv(output_summary, index=False)

    print("Analysis complete.")
    return filtered_df


def analyze_msit_responses(df, output_summary):
    print("Filtering no response and incorrect response trials...")
    filtered_df = df[(df['response'] == 'No Response') | (df['correct'] == False)].copy()

    print("Adding previous trial's correct answer for comparison...")
    filtered_df['previous_correct_answer'] = df['correct'].shift(1)

    print("Comparing current correct answer with previous correct answer...")
    filtered_df['matches_previous'] = filtered_df['correct'] == filtered_df['previous_correct_answer']

    print(f"Saving analyzed data to {output_summary}...")
    filtered_df.to_csv(output_summary, index=False)

    print("Analysis complete.")
    return filtered_df


# User choice
choice = input("Analyze logs for MSIT or RIFG? (m/r): ").strip().lower()
if choice == 'm':
    data_directory = settings.MSIT_LOG_DIR
    summary_directory = settings.MSIT_ANALYZED_LOGS_DIR
    file_path = FileHandler.get_most_recent(action="txt_output_log", log_dir=data_directory)
    log_df = parse_msit_log(file_path)
    analyze_func = analyze_msit_responses
elif choice == 'r':
    data_directory = settings.RIFG_LOG_DIR
    summary_directory = settings.RIFG_ANALYZED_LOGS_DIR
    file_path = FileHandler.get_most_recent(action="txt_output_log", log_dir=data_directory)
    log_df = parse_rifg_log(file_path)
    analyze_func = analyze_rifg_responses
else:
    raise ValueError("Invalid choice. Please enter 'm' for MSIT or 'r' for RIFG.")

latest_filename = os.path.basename(file_path).replace('.txt', '.csv')
output_summary = os.path.join(summary_directory, f"prelim_analysis_{latest_filename}")

os.makedirs(summary_directory, exist_ok=True)
result_df = analyze_func(log_df, output_summary)
