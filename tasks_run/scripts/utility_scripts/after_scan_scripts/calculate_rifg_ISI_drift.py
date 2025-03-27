import pandas as pd
from datetime import datetime
import os
import sys

sys.path.append("/workdir/tasks_run/scripts")
import settings
import FileHandler

def parse_trials_from_log(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    trial_data = []
    current_trial = {}
    in_trial = False

    for line in lines:
        line = line.strip()

        if line.startswith("====== trial"):
            if current_trial:
                trial_data.append(current_trial)
            current_trial = {}
            in_trial = True

        elif in_trial and "," in line:
            key, value = line.split(",", 1)
            current_trial[key.strip()] = value.strip()

    if current_trial:
        trial_data.append(current_trial)

    parsed = []
    for i, trial in enumerate(trial_data):
        try:
            parsed.append({
                "trial": i + 1,
                "starting_trial_time": datetime.fromisoformat(trial["starting_trial_time"]),
                "isi": float(trial["isi"]),
            })
        except Exception as e:
            print(f"Skipping trial {i+1} due to error: {e}")

    return pd.DataFrame(parsed)

def compute_isi_drift(df):
    if "starting_trial_time" not in df.columns:
        raise ValueError("Column 'starting_trial_time' not found in DataFrame.")
    df["actual_diff"] = df["starting_trial_time"].diff().dt.total_seconds()
    df["expected_diff"] = df["isi"].shift(1) + 0.5
    df["drift"] = df["actual_diff"] - df["expected_diff"]
    return df

data_directory = settings.RIFG_LOG_DIR
output_directory = settings.ISI_DRIFT_ANALYSIS_OUTPUT_DIR
if not os.path.exists(output_directory):
    os.makedirs(output_directory, exist_ok=True)
file_path = FileHandler.get_most_recent(action="csv_output_log", log_dir=data_directory)

df = parse_trials_from_log(file_path)
df = compute_isi_drift(df)

base_filename = os.path.basename(file_path)
output_filename = f"ISI_analysis_{base_filename}"
output_path = os.path.join(output_directory, output_filename)

df.to_csv(output_path, index=False)
print(f"ISI drift analysis saved to: {output_path}")
