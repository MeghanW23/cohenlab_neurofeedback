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
    press_isi_pattern = re.compile(r'Pressed ([A-C]) at ([\d.]+) sec into ISI duration')
    press_stimulus_pattern = re.compile(r'Pressed ([A-C]) at ([\d.]+) sec into stimulus presentation')
    result_pattern = re.compile(r'Result:\s*(.+)')

    with open(file_path, 'r') as file:
        lines = file.readlines()

    current_trial = {}
    for line in lines:
        trial_match = trial_pattern.search(line)
        if trial_match:
            if current_trial:
                trials.append(current_trial)
            current_trial = {
                'trial': int(trial_match.group(1)),
                'stimulus': None,
                'isi_presses': [],
                'stimulus_presses': [],
                'result': None
            }
            continue

        stimulus_match = stimulus_pattern.search(line)
        if stimulus_match:
            current_trial['stimulus'] = stimulus_match.group(1)
            continue

        press_isi = press_isi_pattern.search(line)
        if press_isi:
            current_trial['isi_presses'].append({
                'key': press_isi.group(1),
                'time': float(press_isi.group(2))
            })
            continue

        press_stim = press_stimulus_pattern.search(line)
        if press_stim:
            current_trial['stimulus_presses'].append({
                'key': press_stim.group(1),
                'time': float(press_stim.group(2))
            })
            continue

        result_match = result_pattern.search(line)
        if result_match:
            current_trial['result'] = result_match.group(1).strip()
            continue

    if current_trial:
        trials.append(current_trial)

    df = pd.DataFrame([{
        'trial': t['trial'],
        'stimulus': t['stimulus'],
        'result': t['result'],
        'stimulus_press_count': len(t['stimulus_presses']),
        'isi_press_count': len(t['isi_presses']),
        'stimulus_presses': t['stimulus_presses'][0]['key'] if t['stimulus_presses'] else None,
        'stimulus_press_time': t['stimulus_presses'][0]['time'] if t['stimulus_presses'] else None,
        'isi_presses': t['isi_presses'][0]['key'] if t['isi_presses'] else None,
        'isi_press_time': t['isi_presses'][0]['time'] if t['isi_presses'] else None,
        'response_phase': (
            'stimulus' if t['stimulus_presses'] else
            'isi' if t['isi_presses'] else
            'none'
        ),
        'multiple_stimulus_presses': len(t['stimulus_presses']) > 1,
        'multiple_isi_presses': len(t['isi_presses']) > 1
    } for t in trials])

    print("Parsed RIFG DataFrame (first 10 rows):")
    print(df.head(10))
    return df

def analyze_rifg_responses(df, output_summary):
    print("Analyzing RIFG response data...")

    if 'result' not in df.columns:
        raise KeyError("Column 'result' is missing from parsed data.")

    filtered_df = df[df['result'].isin(['false_alarm', 'hit'])].copy()
    filtered_df['previous_trial_result'] = df['result'].shift(1)

    filtered_df['correct_but_wrong_phase'] = (
        (filtered_df['result'] == 'hit') &
        (filtered_df['stimulus_press_count'] == 0) &
        (filtered_df['isi_press_count'] > 0)
    )

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

