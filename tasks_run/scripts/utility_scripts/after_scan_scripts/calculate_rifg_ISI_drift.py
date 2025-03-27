import pandas as pd
from datetime import datetime
import sys

sys.path.append("/workdir/tasks_run/scripts")
import settings
import FileHandler

data_directory = settings.RIFG_LOG_DIR
output_directory = settings.RIFG_ANALYZED_LOGS_DIR
file_path = FileHandler.get_most_recent(action="csv_output_log", log_dir=data_directory)

with open (file_path, 'r') as file:
    lines = file.readlines()

trial_data = []
current_trial = []
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

parsed_trials = []
for i, trial in enumerate(trial_data):
    start_time = datetime.fromisoformat(trial.get("starting_trial_time"))
    isi = float(trial.get("isi", 0))
    parsed_trials.append({
        "trial": i + 1,
        "starting_trial_time": start_time,
        "isi": isi
    })
df = pd.DataFrame(parsed_trials)

df["actual_diff"] = df["starting_trial_time"].diff().dt.total_seconds()
df["expected_diff"] = df["isi"].shift(1) + 0.5
df["drift"] = df["actual_diff"] - df["expected_diff"]

print(df[["trial", "starting_trial_time", "isi", "actual_diff", "expected_diff", "drift"]])